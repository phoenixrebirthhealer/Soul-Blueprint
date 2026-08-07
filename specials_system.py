"""
Phoenix Rebirth | soulReady — Specials Booking System
Railway API endpoints for the reusable "Specials" page (specials.php):

  POST /specials/slots          — dynamically generated available start times for a service type
  GET  /specials/status         — expiration + remaining-capacity info for the page banner
  POST /specials/create-order   — reserve a chosen time, create PayPal order
  POST /specials/capture-order  — capture payment, confirm booking, fire Google Calendar

Writes to its own `specials_bookings` table (see create_specials_bookings_table.sql)
so this data never mixes with your regular `bookings`/`readings` records.

HOW TO RUN A NEW SPECIAL:
Edit the three constants below (SPECIAL_WINDOWS, SPECIAL_SERVICES, SPECIAL_EXPIRES_UTC)
and redeploy. Nothing else needs to change for a new round of specials.
"""

import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from flask import request, jsonify

from booking_system import (
    _get_db,
    paypal_create_order,
    paypal_capture_order,
    create_calendar_event,
    send_confirmation_email,
)

MT_ZONE = ZoneInfo('America/Denver')

# How long a "pending_payment" reservation holds a time before it's treated
# as abandoned and that time becomes bookable again.
PENDING_HOLD_MINUTES = 15

# Granularity for candidate start times within an open window.
SLOT_STEP_MINUTES = 15

# ---------------------------------------------------------------------------
# EDIT THESE FOR EACH NEW SPECIAL
# ---------------------------------------------------------------------------

# Open windows, in Mountain Time. The client can book ANY start time within
# these windows (subject to duration + buffer fitting, and not overlapping
# another booked session of either type).
SPECIAL_WINDOWS = [
    {'date': '2026-08-07', 'start': '12:00', 'end': '17:00'},
    {'date': '2026-08-08', 'start': '08:00', 'end': '12:00'},
    {'date': '2026-08-09', 'start': '08:00', 'end': '14:00'},
    {'date': '2026-08-10', 'start': '10:00', 'end': '17:00'},
    {'date': '2026-08-11', 'start': '10:00', 'end': '17:00'},
    {'date': '2026-08-12', 'start': '08:00', 'end': '14:00'},
]

# Each service type this special offers, its price, its own duration/buffer,
# and how many total slots are available across the whole special.
SPECIAL_SERVICES = {
    'healing': {
        'name': 'Healing Session (Special)',
        'price_cents': 7500,
        'duration_minutes': 90,
        'buffer_minutes': 15,
        'cap': 5,
    },
    'oracle': {
        'name': 'Multidimensional Oracle Reading (Special)',
        'price_cents': 4500,
        'duration_minutes': 60,
        'buffer_minutes': 15,
        'cap': 10,
    },
}

# Booking closes at this UTC instant. 10:00 AM MDT on 8/12/2026 = 16:00 UTC
# (Mountain time is UTC-6 in August, daylight saving). Already-confirmed
# bookings for later that day still happen; this only stops NEW bookings.
SPECIAL_EXPIRES_UTC = datetime(2026, 8, 12, 16, 0, 0, tzinfo=timezone.utc)

# ---------------------------------------------------------------------------
# Capacity + overlap helpers
# ---------------------------------------------------------------------------

def _active_rows(cursor, service_type=None):
    """Rows counted as 'holding' a slot: confirmed, or pending and still fresh."""
    now = datetime.utcnow()
    if service_type:
        cursor.execute(
            "SELECT service_type, slot_utc, service_duration_minutes, status, created_at "
            "FROM specials_bookings WHERE service_type = %s",
            (service_type,),
        )
    else:
        cursor.execute(
            "SELECT service_type, slot_utc, service_duration_minutes, status, created_at "
            "FROM specials_bookings"
        )
    rows = []
    for st, slot_utc, duration, status, created_at in cursor.fetchall():
        if status == 'confirmed':
            rows.append((st, slot_utc, duration, status))
        elif status == 'pending_payment':
            age_minutes = (now - created_at).total_seconds() / 60
            if age_minutes < PENDING_HOLD_MINUTES:
                rows.append((st, slot_utc, duration, status))
    return rows


def _remaining_capacity(cursor, service_type):
    cap = SPECIAL_SERVICES[service_type]['cap']
    used = len(_active_rows(cursor, service_type))
    return max(0, cap - used)


def _booked_blocks(cursor):
    """
    All currently-held time blocks (any service type), as (start_utc, end_utc_with_buffer).
    Confirmed bookings block their duration + the 15-min buffer.
    Pending (in-checkout) bookings only block their exact duration, no buffer,
    and only while the 15-min checkout hold is still fresh (see _active_rows).
    """
    blocks = []
    for st, slot_utc, duration, status in _active_rows(cursor):
        start = slot_utc.replace(tzinfo=timezone.utc)
        if status == 'confirmed':
            buffer = SPECIAL_SERVICES.get(st, {}).get('buffer_minutes', 15)
            end = start + timedelta(minutes=duration + buffer)
        else:
            end = start + timedelta(minutes=duration)
        blocks.append((start, end))
    return blocks


def _has_conflict(booked_blocks, candidate_start_utc, duration, buffer):
    candidate_end_with_buffer = candidate_start_utc + timedelta(minutes=duration + buffer)
    for b_start, b_end in booked_blocks:
        if candidate_start_utc < b_end and candidate_end_with_buffer > b_start:
            return True
    return False


# ---------------------------------------------------------------------------
# Dynamic slot generation
# ---------------------------------------------------------------------------

def generate_available_slots(service_type):
    """Returns (meta_dict, slots_list). meta_dict carries expired/sold_out/remaining info."""
    if service_type not in SPECIAL_SERVICES:
        return {'error': 'Unknown service type'}, []

    now_utc = datetime.now(timezone.utc)
    if now_utc >= SPECIAL_EXPIRES_UTC:
        return {'expired': True, 'remaining': 0}, []

    svc = SPECIAL_SERVICES[service_type]
    conn = _get_db()
    try:
        cursor = conn.cursor()
        remaining = _remaining_capacity(cursor, service_type)
        if remaining <= 0:
            cursor.close()
            return {'sold_out': True, 'remaining': 0}, []
        booked_blocks = _booked_blocks(cursor)
        cursor.close()
    finally:
        conn.close()

    duration = svc['duration_minutes']
    buffer = svc['buffer_minutes']
    min_lead_utc = now_utc + timedelta(hours=1)  # don't offer times less than 1hr out
    slots = []

    for win in SPECIAL_WINDOWS:
        y, m, d = (int(x) for x in win['date'].split('-'))
        sh, sm = (int(x) for x in win['start'].split(':'))
        eh, em = (int(x) for x in win['end'].split(':'))
        win_start_mt = datetime(y, m, d, sh, sm, tzinfo=MT_ZONE)
        win_end_mt = datetime(y, m, d, eh, em, tzinfo=MT_ZONE)

        cursor_mt = win_start_mt
        while True:
            candidate_end_mt = cursor_mt + timedelta(minutes=duration)
            if candidate_end_mt > win_end_mt:
                break

            candidate_start_utc = cursor_mt.astimezone(timezone.utc)
            if candidate_start_utc >= min_lead_utc:
                if not _has_conflict(booked_blocks, candidate_start_utc, duration, buffer):
                    slots.append({
                        'utc': candidate_start_utc.strftime('%Y-%m-%d %H:%M:%S'),
                        'date': win['date'],
                        'mt_display': cursor_mt.strftime('%A, %B %-d — %-I:%M %p MT'),
                        'time_label': cursor_mt.strftime('%-I:%M %p'),
                    })
            cursor_mt += timedelta(minutes=SLOT_STEP_MINUTES)

    return {'remaining': remaining}, slots


# ---------------------------------------------------------------------------
# Booking write path
# ---------------------------------------------------------------------------

def _reserve_slot(data):
    """
    Validates capacity + overlap fresh (in case of a race with another buyer),
    then inserts a pending_payment row holding this exact time.
    Returns the new row id, or None if the time is no longer available.
    """
    service_type = data['service_type']
    svc = SPECIAL_SERVICES[service_type]
    slot_utc_dt = datetime.strptime(data['slot_utc'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

    conn = _get_db()
    cursor = conn.cursor()
    try:
        if _remaining_capacity(cursor, service_type) <= 0:
            return None
        booked_blocks = _booked_blocks(cursor)
        if _has_conflict(booked_blocks, slot_utc_dt, svc['duration_minutes'], svc['buffer_minutes']):
            return None

        cursor.execute("""
            INSERT INTO specials_bookings (
                client_name, client_email, client_phone, service_name, service_type,
                service_price_cents, service_duration_minutes, slot_label, slot_utc,
                slot_mt_display, client_timezone, slot_client_display, status
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, 'pending_payment'
            )
        """, (
            data['client_name'],
            data['client_email'],
            data.get('client_phone'),
            svc['name'],
            service_type,
            svc['price_cents'],
            svc['duration_minutes'],
            data.get('slot_label'),
            data['slot_utc'],
            data.get('slot_mt_display'),
            data.get('client_timezone'),
            data.get('slot_client_display'),
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def _attach_order_id(row_id, order_id):
    conn = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE specials_bookings SET paypal_order_id = %s WHERE id = %s",
            (order_id, row_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def _delete_row(row_id):
    conn = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM specials_bookings WHERE id = %s", (row_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def _find_pending_by_order(order_id):
    conn = _get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM specials_bookings WHERE paypal_order_id = %s AND status = 'pending_payment'",
            (order_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def _confirm_booking(row_id, capture_id, gcal_event_id, meet_link):
    conn = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE specials_bookings
            SET status = 'confirmed',
                paypal_capture_id = %s,
                google_calendar_event_id = %s,
                google_meet_link = %s
            WHERE id = %s
        """, (capture_id, gcal_event_id, meet_link, row_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Plain callable functions (no Flask dependency)
#
# These are the ones actually used by local_api.py, which handles routes
# itself and does not use Flask. They are also used by the optional
# register_specials_routes(app) Flask wrapper below, kept in case a Flask
# app is ever the real entry point later.
# ---------------------------------------------------------------------------

class SpecialsError(Exception):
    """Raised for any expected/user-facing error. .status_code mirrors the
    HTTP status this should be reported as, whichever server framework is
    actually calling this code."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def get_specials_status():
    now_utc = datetime.now(timezone.utc)
    expired = now_utc >= SPECIAL_EXPIRES_UTC
    remaining = {}
    if not expired:
        conn = _get_db()
        cursor = conn.cursor()
        try:
            for t in SPECIAL_SERVICES:
                remaining[t] = _remaining_capacity(cursor, t)
        finally:
            cursor.close()
            conn.close()
    else:
        remaining = {t: 0 for t in SPECIAL_SERVICES}

    return {
        'expired': expired,
        'expires_utc': SPECIAL_EXPIRES_UTC.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'remaining': remaining,
        'services': {
            t: {'name': s['name'], 'price_cents': s['price_cents'],
                'duration_minutes': s['duration_minutes'], 'cap': s['cap']}
            for t, s in SPECIAL_SERVICES.items()
        },
    }


def get_specials_slots(service_type):
    """Returns {"slots": [...], "remaining": N, ...}. Raises SpecialsError on bad input."""
    if not service_type:
        raise SpecialsError('service_type is required', 400)
    if service_type not in SPECIAL_SERVICES:
        raise SpecialsError('Unknown service type', 400)
    meta, slots = generate_available_slots(service_type)
    if meta.get('error'):
        raise SpecialsError(meta['error'], 400)
    return {**meta, 'slots': slots}


def create_specials_order(data):
    """
    data keys: service_type, slot_utc, slot_label, slot_mt_display,
    slot_client_display, client_timezone, client_name, client_email,
    client_phone, return_url, cancel_url.
    Returns {"order_id": "...", "approval_url": "..."}. Raises SpecialsError.
    """
    required = ['service_type', 'slot_utc', 'client_name', 'client_email',
                'return_url', 'cancel_url']
    missing = [f for f in required if not data.get(f)]
    if missing:
        raise SpecialsError(f"Missing fields: {', '.join(missing)}", 400)

    service_type = data['service_type']
    if service_type not in SPECIAL_SERVICES:
        raise SpecialsError('Unknown service type', 400)

    if datetime.now(timezone.utc) >= SPECIAL_EXPIRES_UTC:
        raise SpecialsError('This special has closed and is no longer accepting new bookings.', 410)

    svc = SPECIAL_SERVICES[service_type]

    try:
        row_id = _reserve_slot(data)
    except Exception as exc:
        raise SpecialsError(f"Could not reserve that time: {str(exc)}", 500)

    if row_id is None:
        raise SpecialsError('That time is no longer available. Please choose another.', 409)

    try:
        order_id, approval_url = paypal_create_order(
            svc['price_cents'],
            f"Phoenix Rebirth Special | {svc['name']}",
            data['return_url'],
            data['cancel_url'],
        )
        _attach_order_id(row_id, order_id)
        return {'order_id': order_id, 'approval_url': approval_url}
    except Exception as exc:
        _delete_row(row_id)  # release the hold if PayPal failed
        raise SpecialsError(str(exc), 500)


def capture_specials_order(order_id):
    """Returns the confirmed booking details dict. Raises SpecialsError."""
    if not order_id:
        raise SpecialsError('order_id is required', 400)

    booking = _find_pending_by_order(order_id)
    if not booking:
        raise SpecialsError('No pending booking found for this order. If you were charged, please contact Christina.', 404)

    try:
        capture_id = paypal_capture_order(order_id)
    except Exception as exc:
        raise SpecialsError(f"PayPal capture failed: {str(exc)}", 502)

    gcal_event_id = None
    meet_link = None
    try:
        gcal_event_id, meet_link = create_calendar_event(
            booking['slot_utc'].strftime('%Y-%m-%d %H:%M:%S'),
            booking['service_duration_minutes'],
            f"Phoenix Rebirth Special | {booking['service_name']} — {booking['client_name']}",
            f"Client: {booking['client_name']}\nEmail: {booking['client_email']}\nService: {booking['service_name']}",
            booking['client_email'],
        )
    except Exception:
        pass  # Calendar failure does not block the booking

    try:
        _confirm_booking(booking['id'], capture_id, gcal_event_id, meet_link)
    except Exception as exc:
        raise SpecialsError(f"Booking confirmation save failed: {str(exc)}", 500)

    try:
        send_confirmation_email(
            booking['client_email'], booking['client_name'], booking['service_name'],
            booking.get('slot_mt_display') or 'Time TBD', meet_link,
        )
    except Exception:
        pass

    return {
        'status': 'confirmed',
        'meet_link': meet_link,
        'order_id': order_id,
        'service_name': booking['service_name'],
        'client_name': booking['client_name'],
        'client_email': booking['client_email'],
        'charged_price_cents': booking['service_price_cents'],
        'slot_mt_display': booking.get('slot_mt_display'),
    }


# ---------------------------------------------------------------------------
# Optional Flask wrapper (NOT used by local_api.py — kept only in case a
# Flask app ever becomes the real entry point). If your live server is
# local_api.py, ignore this section entirely; it is not called.
# ---------------------------------------------------------------------------

def register_specials_routes(app):

    @app.route('/specials/status', methods=['GET'])
    def specials_status():
        return jsonify(get_specials_status())

    @app.route('/specials/slots', methods=['POST'])
    def specials_slots():
        data = request.get_json(force=True, silent=True) or {}
        try:
            return jsonify(get_specials_slots(data.get('service_type')))
        except SpecialsError as e:
            return jsonify({'error': e.message}), e.status_code

    @app.route('/specials/create-order', methods=['POST'])
    def specials_create():
        data = request.get_json(force=True, silent=True) or {}
        try:
            return jsonify(create_specials_order(data))
        except SpecialsError as e:
            return jsonify({'error': e.message}), e.status_code

    @app.route('/specials/capture-order', methods=['POST'])
    def specials_capture():
        data = request.get_json(force=True, silent=True) or {}
        try:
            return jsonify(capture_specials_order(data.get('order_id')))
        except SpecialsError as e:
            return jsonify({'error': e.message}), e.status_code
