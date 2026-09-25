"""
Phoenix Rebirth | soulReady — Booking System
Railway API endpoints for:
  POST /slots                 — existing general availability
  POST /practitioner-slots   — practitioner-specific availability
  POST /ffs-credit            — unused Field Frequency Scan credit check
  POST /paypal/create-order   — create PayPal order and reserve practitioner slot
  POST /paypal/capture-order  — capture payment, save booking, fire Google Calendar

This version preserves the existing general booking schedule while adding
server-side practitioner authorization and practitioner-specific slot locking.
"""

import hashlib
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo

import requests
from flask import request, jsonify

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_db():
    import mysql.connector
    return mysql.connector.connect(
        host=os.environ['MYSQL_HOST'],
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        database=os.environ['MYSQL_DATABASE'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        autocommit=False,
        connection_timeout=10,
    )


# ---------------------------------------------------------------------------
# Canonical practitioner-booking services
# ---------------------------------------------------------------------------

PRACTITIONER_SERVICES = {
    'field_frequency_scan': {
        'name': 'Field Frequency Scan', 'price_cents': 7500,
        'duration_minutes': 60, 'buffer_minutes': 0,
    },
    'aura_cleansing': {
        'name': 'Aura Cleansing', 'price_cents': 4000,
        'duration_minutes': 30, 'buffer_minutes': 15,
    },
    'rapid_relief': {
        'name': 'Rapid Relief Session', 'price_cents': 22500,
        'duration_minutes': 60, 'buffer_minutes': 0,
    },
    'mild_healing': {
        'name': 'Mild Healing', 'price_cents': 27500,
        'duration_minutes': 90, 'buffer_minutes': 0,
    },
    'foundational_energy': {
        'name': 'Foundational Energy Healing', 'price_cents': 17000,
        'duration_minutes': 120, 'buffer_minutes': 15,
    },
    'chronic_healing': {
        'name': 'Chronic Healing', 'price_cents': 47500,
        'duration_minutes': 120, 'buffer_minutes': 0,
    },
    'guidance': {
        'name': 'Guidance Session', 'price_cents': 45000,
        'duration_minutes': 90, 'buffer_minutes': 0,
    },
    'sovereign_oracle': {
        'name': 'Sovereign Multidimensional Oracle Reading', 'price_cents': 57500,
        'duration_minutes': 90, 'buffer_minutes': 0,
    },
    'soul_core_alignment': {
        'name': 'Soul Core Alignment', 'price_cents': 100000,
        'duration_minutes': 120, 'buffer_minutes': 0,
    },
}

MT_ZONE = ZoneInfo('America/Denver')
VALID_WEEKDAYS = {1, 2, 4, 5}
SLOT_DURATION_MINUTES = 60
SLOT_INTERVAL_MINUTES = 60


def _service(service_key):
    return PRACTITIONER_SERVICES.get(str(service_key or '').strip())


def _parse_utc_slot(value):
    """Accept the legacy SQL format or ISO-8601 Z format and return UTC datetime."""
    if not value:
        return None
    raw = str(value).strip()
    try:
        if raw.endswith('Z'):
            return datetime.fromisoformat(raw[:-1]).replace(tzinfo=timezone.utc)
        dt = datetime.strptime(raw, '%Y-%m-%d %H:%M:%S')
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _format_utc_slot(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


# ---------------------------------------------------------------------------
# Existing general slot generation
# ---------------------------------------------------------------------------

def _get_schedule(cursor):
    cursor.execute(
        "SELECT day_of_week, start_time, end_time FROM availability_schedule WHERE is_active = 1"
    )
    schedule = {}
    for row in cursor.fetchall():
        dow, start, end = row
        schedule[int(dow)] = {
            'start': (int(start.seconds // 3600), int((start.seconds % 3600) // 60)),
            'end': (int(end.seconds // 3600), int((end.seconds % 3600) // 60)),
        }
    return schedule


def _get_blocks(cursor, year, month):
    cursor.execute(
        "SELECT block_date FROM availability_blocks "
        "WHERE YEAR(block_date) = %s AND MONTH(block_date) = %s",
        (year, month),
    )
    return {row[0] for row in cursor.fetchall()}


def _get_booked_slots(cursor, year, month):
    cursor.execute(
        "SELECT slot_utc FROM bookings "
        "WHERE YEAR(slot_utc) = %s AND MONTH(slot_utc) = %s "
        "AND status IN ('confirmed', 'pending_payment')",
        (year, month),
    )
    return {row[0] for row in cursor.fetchall() if row[0]}


def generate_slots_for_month(year, month):
    conn = _get_db()
    try:
        cursor = conn.cursor()
        schedule = _get_schedule(cursor)
        blocked = _get_blocks(cursor, year, month)
        booked_utc = _get_booked_slots(cursor, year, month)
        cursor.close()
    finally:
        conn.close()

    now_mt = datetime.now(MT_ZONE)
    slots = []
    d = date(year, month, 1)
    while d.month == month:
        py_dow = d.weekday()
        mysql_dow = (py_dow + 1) % 7
        if mysql_dow in schedule and d not in blocked:
            sched = schedule[mysql_dow]
            sh, sm = sched['start']
            eh, em = sched['end']
            slot_dt = datetime(year, d.month, d.day, sh, sm, tzinfo=MT_ZONE)
            end_dt = datetime(year, d.month, d.day, eh, em, tzinfo=MT_ZONE)
            while slot_dt + timedelta(minutes=SLOT_DURATION_MINUTES) <= end_dt:
                if slot_dt > now_mt + timedelta(hours=1):
                    utc_dt = slot_dt.astimezone(timezone.utc)
                    utc_str = utc_dt.strftime('%Y-%m-%d %H:%M:%S')
                    if utc_str not in booked_utc:
                        slots.append({
                            'utc': utc_str,
                            'mt': slot_dt.strftime('%Y-%m-%d %H:%M'),
                            'label': slot_dt.strftime('%-I:%M %p MT'),
                            'date': d.isoformat(),
                            'weekday': d.strftime('%A'),
                        })
                slot_dt += timedelta(minutes=SLOT_INTERVAL_MINUTES)
        d += timedelta(days=1)
    return slots


# ---------------------------------------------------------------------------
# Practitioner availability / collision checks
# ---------------------------------------------------------------------------

def _practitioner_is_authorized(cursor, practitioner_id, service_key):
    cursor.execute(
        "SELECT p.display_name FROM practitioners p "
        "INNER JOIN phoenix_service_practitioners sp ON sp.practitioner_id=p.id "
        "WHERE p.id=%s AND p.is_active=1 AND sp.service_key=%s AND sp.active=1 LIMIT 1",
        (practitioner_id, service_key),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def _load_busy_intervals(cursor, practitioner_id):
    """Return occupied UTC intervals for confirmed/pending bookings and active holds."""
    busy = []
    cursor.execute(
        "SELECT slot_utc, service_key FROM bookings "
        "WHERE practitioner_id=%s AND status IN ('confirmed','pending_payment')",
        (practitioner_id,),
    )
    for slot, key in cursor.fetchall():
        if not slot:
            continue
        start_dt = slot.replace(tzinfo=timezone.utc) if hasattr(slot, 'replace') else _parse_utc_slot(str(slot))
        svc = _service(key)
        minutes = (svc['duration_minutes'] + svc['buffer_minutes']) if svc else 60
        if start_dt:
            busy.append((start_dt, start_dt + timedelta(minutes=minutes)))

    cursor.execute(
        "SELECT slot_utc, service_key FROM phoenix_booking_holds "
        "WHERE practitioner_id=%s AND status='held' AND expires_at > UTC_TIMESTAMP()",
        (practitioner_id,),
    )
    for slot, key in cursor.fetchall():
        if not slot:
            continue
        start_dt = slot.replace(tzinfo=timezone.utc) if hasattr(slot, 'replace') else _parse_utc_slot(str(slot))
        svc = _service(key)
        minutes = (svc['duration_minutes'] + svc['buffer_minutes']) if svc else 60
        if start_dt:
            busy.append((start_dt, start_dt + timedelta(minutes=minutes)))
    return busy


def _slot_is_available(cursor, practitioner_id, slot_utc, calendar_minutes):
    start_dt = _parse_utc_slot(slot_utc)
    if start_dt is None:
        return False
    end_dt = start_dt + timedelta(minutes=calendar_minutes)
    for busy_start, busy_end in _load_busy_intervals(cursor, practitioner_id):
        if start_dt < busy_end and end_dt > busy_start:
            return False
    return True


def _slot_within_practitioner_availability(cursor, practitioner_id, slot_utc, calendar_minutes):
    utc_dt = _parse_utc_slot(slot_utc)
    if utc_dt is None:
        return False
    local_dt = utc_dt.astimezone(MT_ZONE)
    weekday = int(local_dt.strftime('%w'))  # Sunday=0, matching the PHP table.
    start = local_dt.strftime('%H:%M:%S')
    end = (local_dt + timedelta(minutes=calendar_minutes)).strftime('%H:%M:%S')
    cursor.execute(
        "SELECT 1 FROM phoenix_practitioner_availability "
        "WHERE practitioner_id=%s AND weekday=%s AND active=1 "
        "AND start_time <= %s AND end_time >= %s LIMIT 1",
        (practitioner_id, weekday, start, end),
    )
    return cursor.fetchone() is not None


def generate_practitioner_slots_for_month(year, month, practitioner_id, service_key):
    svc = _service(service_key)
    if not svc:
        raise ValueError('That service is not configured for practitioner booking.')

    calendar_minutes = svc['duration_minutes'] + svc['buffer_minutes']
    conn = _get_db()
    try:
        cursor = conn.cursor()
        name = _practitioner_is_authorized(cursor, practitioner_id, service_key)
        if not name:
            raise ValueError('This practitioner is not authorized for the selected service.')

        cursor.execute(
            "SELECT weekday,start_time,end_time FROM phoenix_practitioner_availability "
            "WHERE practitioner_id=%s AND active=1 ORDER BY weekday,start_time",
            (practitioner_id,),
        )
        windows = cursor.fetchall()

        busy_intervals = _load_busy_intervals(cursor, practitioner_id)

        by_weekday = {}
        for weekday, start_time, end_time in windows:
            by_weekday.setdefault(int(weekday), []).append((start_time, end_time))

        now_mt = datetime.now(MT_ZONE)
        slots = []
        days = __import__('calendar').monthrange(year, month)[1]
        for day in range(1, days + 1):
            local_date = date(year, month, day)
            weekday = int(local_date.strftime('%w'))
            for start_time, end_time in by_weekday.get(weekday, []):
                sh, sm = map(int, str(start_time)[:5].split(':'))
                eh, em = map(int, str(end_time)[:5].split(':'))
                slot_dt = datetime(year, month, day, sh, sm, tzinfo=MT_ZONE)
                end_dt = datetime(year, month, day, eh, em, tzinfo=MT_ZONE)
                while slot_dt + timedelta(minutes=calendar_minutes) <= end_dt:
                    if slot_dt > now_mt + timedelta(hours=1):
                        utc_dt = slot_dt.astimezone(timezone.utc)
                        utc_str = _format_utc_slot(utc_dt)
                        candidate_end = utc_dt + timedelta(minutes=calendar_minutes)
                        overlaps = any(utc_dt < busy_end and candidate_end > busy_start for busy_start, busy_end in busy_intervals)
                        if not overlaps:
                            slots.append({
                                'utc': utc_str,
                                'mt': slot_dt.strftime('%Y-%m-%d %H:%M'),
                                'label': slot_dt.strftime('%-I:%M %p MT'),
                                'date': local_date.isoformat(),
                                'weekday': local_date.strftime('%A'),
                            })
                    slot_dt += timedelta(minutes=30)
        return slots
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# PayPal helpers
# ---------------------------------------------------------------------------

def _paypal_base():
    return 'https://api-m.sandbox.paypal.com' if os.environ.get('PAYPAL_MODE', 'live') == 'sandbox' else 'https://api-m.paypal.com'


def _paypal_token():
    resp = requests.post(
        f"{_paypal_base()}/v1/oauth2/token",
        auth=(os.environ['PAYPAL_CLIENT_ID'], os.environ['PAYPAL_CLIENT_SECRET']),
        data={'grant_type': 'client_credentials'}, timeout=15,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def paypal_create_order(amount_cents, description, return_url, cancel_url):
    token = _paypal_token()
    amount = f"{amount_cents / 100:.2f}"
    payload = {
        'intent': 'CAPTURE',
        'purchase_units': [{'amount': {'currency_code': 'USD', 'value': amount}, 'description': description}],
        'application_context': {
            'return_url': return_url, 'cancel_url': cancel_url,
            'shipping_preference': 'NO_SHIPPING', 'user_action': 'PAY_NOW',
        },
    }
    resp = requests.post(
        f"{_paypal_base()}/v2/checkout/orders",
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json=payload, timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    return data['id'], next((link['href'] for link in data.get('links', []) if link['rel'] == 'approve'), None)


def paypal_capture_order(order_id):
    token = _paypal_token()
    resp = requests.post(
        f"{_paypal_base()}/v2/checkout/orders/{order_id}/capture",
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    capture_id = data['purchase_units'][0]['payments']['captures'][0]['id']
    return capture_id


# ---------------------------------------------------------------------------
# Google Calendar helpers
# ---------------------------------------------------------------------------

def _gcal_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    sa_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '')
    if not sa_json:
        raise ValueError('GOOGLE_SERVICE_ACCOUNT_JSON env var is not set')
    info = json.loads(sa_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)


def create_calendar_event(slot_utc_str, duration_minutes, summary, description, attendee_email):
    service = _gcal_service()
    calendar_id = os.environ.get('GOOGLE_CALENDAR_ID', 'christina@phoenixrebirth.life')
    start_dt = _parse_utc_slot(slot_utc_str)
    if start_dt is None:
        raise ValueError('Invalid slot_utc')
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'UTC'},
        'attendees': [{'email': attendee_email}],
        'conferenceData': {'createRequest': {
            'requestId': f"phoenix-{start_dt.timestamp():.0f}",
            'conferenceSolutionKey': {'type': 'hangoutsMeet'},
        }},
    }
    result = service.events().insert(calendarId=calendar_id, body=event, conferenceDataVersion=1, sendUpdates='all').execute()
    return result.get('id'), result.get('hangoutLink')


# ---------------------------------------------------------------------------
# Email confirmation
# ---------------------------------------------------------------------------

def send_confirmation_email(to_email, client_name, service_name, slot_mt_display, meet_link, session_type='google_meet', whatsapp_number='', practitioner_name=''):
    confirm_url = os.environ.get('IONOS_CONFIRM_URL')
    secret = os.environ.get('CONFIRM_SECRET')
    if not confirm_url or not secret:
        return
    try:
        payload = json.dumps({
            'client_email': to_email, 'client_name': client_name, 'service_name': service_name,
            'slot_mt_display': slot_mt_display, 'meet_link': meet_link or '',
            'session_type': session_type, 'whatsapp_number': whatsapp_number,
            'practitioner_name': practitioner_name,
        }).encode('utf-8')
        req = urllib.request.Request(confirm_url, data=payload, headers={'Content-Type': 'application/json', 'X-Confirm-Secret': secret})
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Booking DB write
# ---------------------------------------------------------------------------

def save_booking(booking_data):
    conn = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bookings (
                client_name, client_email, service_name, service_price_cents,
                charged_price_cents, ffs_credit_applied, slot_utc, slot_mt,
                client_timezone, slot_client_display, slot_mt_display,
                status, paypal_order_id, paypal_capture_id,
                google_calendar_event_id, google_meet_link, confirmation_email_sent,
                practitioner_id, practitioner_name, service_key
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
        """, (
            booking_data['client_name'], booking_data['client_email'], booking_data['service_name'],
            booking_data['service_price_cents'], booking_data['charged_price_cents'],
            1 if booking_data.get('ffs_credit_applied') else 0, booking_data.get('slot_utc'),
            booking_data.get('slot_mt'), booking_data.get('client_timezone'),
            booking_data.get('slot_client_display'), booking_data.get('slot_mt_display'),
            booking_data.get('status', 'confirmed'), booking_data.get('paypal_order_id'),
            booking_data.get('paypal_capture_id'), booking_data.get('google_calendar_event_id'),
            booking_data.get('google_meet_link'), 1 if booking_data.get('confirmation_email_sent') else 0,
            booking_data.get('practitioner_id'), booking_data.get('practitioner_name'), booking_data.get('service_key'),
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def check_ffs_credit(client_email):
    conn = _get_db(); cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE client_email=%s AND service_name='Field Frequency Scan' "
            "AND status='confirmed' AND ffs_credit_applied=0", (client_email,)
        )
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close(); conn.close()


def _release_hold(cursor, order_id):
    cursor.execute("UPDATE phoenix_booking_holds SET status='released' WHERE hold_token=%s AND status='held'", (order_id,))


# ---------------------------------------------------------------------------
# Practitioner-aware functions used by the existing local_api.py wrapper
# ---------------------------------------------------------------------------

def create_practitioner_order(payload):
    service_key = str(payload.get('service_key', '')).strip()
    svc = _service(service_key)
    if not svc:
        raise ValueError('That service is not configured for practitioner booking.')
    service_name = str(payload.get('service_name', '')).strip()
    price_cents = int(payload.get('service_price_cents', 0))
    ffs_applied = bool(payload.get('ffs_credit_applied', False))
    practitioner_id = int(payload.get('practitioner_id', 0) or 0)
    slot_utc = payload.get('slot_utc')
    return_url = payload.get('return_url')
    cancel_url = payload.get('cancel_url')
    esoteric_token = payload.get('esoteric_token', '')
    if not service_name or not price_cents or not return_url or not cancel_url:
        raise ValueError('service_name, service_price_cents, return_url, cancel_url are required')
    if price_cents != svc['price_cents']:
        raise ValueError('Service price mismatch. Please refresh the booking page.')
    if not practitioner_id or not slot_utc:
        raise ValueError('A practitioner and available time are required.')
    parsed_slot = _parse_utc_slot(slot_utc)
    if parsed_slot is None:
        raise ValueError('Invalid booking time.')
    conn = _get_db(); cursor = conn.cursor()
    try:
        practitioner_name = _practitioner_is_authorized(cursor, practitioner_id, service_key)
        if not practitioner_name:
            raise ValueError('That practitioner is not authorized for this service.')
        minutes = svc['duration_minutes'] + svc['buffer_minutes']
        if not _slot_within_practitioner_availability(cursor, practitioner_id, slot_utc, minutes):
            raise ValueError('That time is outside the practitioner availability.')
        if not _slot_is_available(cursor, practitioner_id, slot_utc, minutes):
            raise ValueError('That time was just taken. Please choose another time.')
        charged_cents = max(0, price_cents - (7500 if ffs_applied else 0))
        if charged_cents == 0:
            raise ValueError('This booking has no PayPal balance after credit. Please contact Phoenix Rebirth to complete it.')
        if esoteric_token:
            sep = '&' if '?' in return_url else '?'
            return_url = f"{return_url}{sep}esoteric_token={esoteric_token}"
        order_id, approval_url = paypal_create_order(
            charged_cents, f"Phoenix Rebirth | {service_name} — {practitioner_name}", return_url, cancel_url
        )
        cursor.execute("DELETE FROM phoenix_booking_holds WHERE status='held' AND expires_at <= UTC_TIMESTAMP()")
        cursor.execute(
            "INSERT INTO phoenix_booking_holds (hold_token, practitioner_id, service_key, slot_utc, expires_at, status) "
            "VALUES (%s,%s,%s,%s,DATE_ADD(UTC_TIMESTAMP(), INTERVAL 15 MINUTE),'held')",
            (order_id, practitioner_id, service_key, _format_utc_slot(parsed_slot)),
        )
        conn.commit()
        return {'order_id':order_id,'approval_url':approval_url,'charged_cents':charged_cents,
                'practitioner_id':practitioner_id,'practitioner_name':practitioner_name,'service_key':service_key}
    except Exception:
        conn.rollback(); raise
    finally:
        cursor.close(); conn.close()


def capture_practitioner_order(payload):
    required = ['order_id','client_name','client_email','service_name','service_price_cents','charged_price_cents']
    missing = [f for f in required if not payload.get(f)]
    if missing: raise ValueError(f"Missing fields: {', '.join(missing)}")
    order_id = payload['order_id']
    service_key = str(payload.get('service_key', '')).strip()
    svc = _service(service_key)
    practitioner_id = int(payload.get('practitioner_id', 0) or 0)
    practitioner_name = payload.get('practitioner_name')
    if not svc or not practitioner_id: raise ValueError('Practitioner booking information is missing or invalid.')
    price_cents = int(payload['service_price_cents']); charged_cents = int(payload['charged_price_cents'])
    expected = max(0, price_cents - (7500 if payload.get('ffs_credit_applied') else 0))
    if price_cents != svc['price_cents'] or charged_cents != expected: raise ValueError('Service price or charged amount mismatch.')
    parsed_slot = _parse_utc_slot(payload.get('slot_utc'))
    if parsed_slot is None: raise ValueError('A valid booking time is required.')
    conn = _get_db(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT practitioner_id,service_key,slot_utc FROM phoenix_booking_holds WHERE hold_token=%s AND status='held' AND expires_at>UTC_TIMESTAMP() FOR UPDATE", (order_id,))
        hold = cursor.fetchone()
        if not hold: raise ValueError('This PayPal booking session expired. Please choose the time again.')
        hold_pid, hold_key, hold_slot = hold
        hold_slot_str = hold_slot.strftime('%Y-%m-%d %H:%M:%S') if hasattr(hold_slot,'strftime') else str(hold_slot)
        if int(hold_pid)!=practitioner_id or hold_key!=service_key or _format_utc_slot(parsed_slot)!=hold_slot_str:
            raise ValueError('The practitioner or booking time does not match the reserved slot.')
        if not _practitioner_is_authorized(cursor, practitioner_id, service_key):
            raise ValueError('That practitioner is no longer authorized for this service.')
        cursor.execute("SELECT 1 FROM bookings WHERE practitioner_id=%s AND slot_utc=%s AND status IN ('confirmed','pending_payment') LIMIT 1", (practitioner_id,hold_slot_str))
        if cursor.fetchone(): raise ValueError('That practitioner slot has already been booked.')
        capture_id = paypal_capture_order(order_id)
        minutes = svc['duration_minutes'] + svc['buffer_minutes']
        gcal_event_id = None; meet_link = None
        try:
            gcal_event_id, meet_link = create_calendar_event(
                hold_slot_str, minutes,
                f"Phoenix Rebirth | {payload['service_name']} — {payload['client_name']}",
                f"Client: {payload['client_name']}\nEmail: {payload['client_email']}\nService: {payload['service_name']}\nPractitioner: {practitioner_name or ''}",
                payload['client_email'])
        except Exception: pass
        booking_id = save_booking({
            'client_name':payload['client_name'],'client_email':payload['client_email'],'service_name':payload['service_name'],
            'service_price_cents':price_cents,'charged_price_cents':charged_cents,'ffs_credit_applied':bool(payload.get('ffs_credit_applied')),
            'slot_utc':hold_slot_str,'slot_mt':payload.get('slot_mt'),'client_timezone':payload.get('client_timezone'),
            'slot_client_display':payload.get('slot_client_display'),'slot_mt_display':payload.get('slot_mt_display'),
            'status':'confirmed','paypal_order_id':order_id,'paypal_capture_id':capture_id,
            'google_calendar_event_id':gcal_event_id,'google_meet_link':meet_link,'confirmation_email_sent':False,
            'practitioner_id':practitioner_id,'practitioner_name':practitioner_name or _practitioner_is_authorized(cursor,practitioner_id,service_key),
            'service_key':service_key})
        cursor.execute("DELETE FROM phoenix_booking_holds WHERE hold_token=%s", (order_id,))
        conn.commit()
        try:
            send_confirmation_email(payload['client_email'],payload['client_name'],payload['service_name'],payload.get('slot_mt_display') or 'Time TBD',meet_link,practitioner_name=practitioner_name or '')
        except Exception: pass
        return {'status':'confirmed','booking_id':booking_id,'meet_link':meet_link,'order_id':order_id}
    except Exception:
        conn.rollback(); raise
    finally:
        cursor.close(); conn.close()

# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

def register_booking_routes(app):

    @app.route('/slots', methods=['POST'])
    def slots():
        data = request.get_json(force=True, silent=True) or {}
        year, month = data.get('year'), data.get('month')
        if not year or not month:
            return jsonify({'error': 'year and month are required'}), 400
        try:
            return jsonify({'slots': generate_slots_for_month(int(year), int(month))})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500

    @app.route('/practitioner-slots', methods=['POST'])
    def practitioner_slots():
        data = request.get_json(force=True, silent=True) or {}
        try:
            practitioner_id = int(data.get('practitioner_id', 0))
            year = int(data.get('year', 0)); month = int(data.get('month', 0))
            service_key = str(data.get('service_key', '')).strip()
            if not practitioner_id or not year or not 1 <= month <= 12:
                raise ValueError('practitioner_id, year and month are required')
            return jsonify({'slots': generate_practitioner_slots_for_month(year, month, practitioner_id, service_key)})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 400

    @app.route('/ffs-credit', methods=['POST'])
    def ffs_credit():
        data = request.get_json(force=True, silent=True) or {}
        email = data.get('email', '').strip().lower()
        if not email:
            return jsonify({'error': 'email is required'}), 400
        try:
            return jsonify({'hasCredit': check_ffs_credit(email)})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500

    @app.route('/paypal/create-order', methods=['POST'])
    def paypal_create():
        data = request.get_json(force=True, silent=True) or {}
        service_key = str(data.get('service_key', '')).strip()
        svc = _service(service_key) if service_key else None
        service_name = data.get('service_name', '')
        price_cents = int(data.get('service_price_cents', 0))
        ffs_applied = bool(data.get('ffs_credit_applied', False))
        practitioner_id = int(data.get('practitioner_id', 0) or 0)
        slot_utc = data.get('slot_utc')
        return_url = data.get('return_url'); cancel_url = data.get('cancel_url')
        esoteric_token = data.get('esoteric_token', '')

        if not service_name or not price_cents or not return_url or not cancel_url:
            return jsonify({'error': 'service_name, service_price_cents, return_url, cancel_url are required'}), 400

        # New practitioner-aware services are validated against the canonical catalog.
        if service_key:
            if not svc:
                return jsonify({'error': 'That service is not configured for practitioner booking.'}), 400
            if price_cents != svc['price_cents']:
                return jsonify({'error': 'Service price mismatch. Please refresh the booking page.'}), 400
            if not practitioner_id or not slot_utc:
                return jsonify({'error': 'A practitioner and available time are required.'}), 400
            if ffs_applied and service_key == 'field_frequency_scan':
                return jsonify({'error': 'A Field Frequency Scan cannot use its own credit.'}), 400

            conn = _get_db(); cursor = conn.cursor()
            try:
                practitioner_name = _practitioner_is_authorized(cursor, practitioner_id, service_key)
                if not practitioner_name:
                    return jsonify({'error': 'That practitioner is not authorized for this service.'}), 403
                parsed_slot = _parse_utc_slot(slot_utc)
                if parsed_slot is None:
                    return jsonify({'error': 'Invalid booking time.'}), 400
                calendar_minutes = svc['duration_minutes'] + svc['buffer_minutes']
                if not _slot_within_practitioner_availability(cursor, practitioner_id, slot_utc, calendar_minutes):
                    return jsonify({'error': 'That time is outside the practitioner availability.'}), 409
                if not _slot_is_available(cursor, practitioner_id, slot_utc, calendar_minutes):
                    return jsonify({'error': 'That time was just taken. Please choose another time.'}), 409

                charged_cents = max(0, price_cents - (7500 if ffs_applied else 0))
                if charged_cents == 0:
                    return jsonify({'error': 'This booking has no PayPal balance after credit. Please contact Phoenix Rebirth to complete it.'}), 400

                if esoteric_token:
                    sep = '&' if '?' in return_url else '?'
                    return_url = f"{return_url}{sep}esoteric_token={esoteric_token}"

                order_id, approval_url = paypal_create_order(
                    charged_cents, f"Phoenix Rebirth | {service_name}", return_url, cancel_url
                )

                cursor.execute("DELETE FROM phoenix_booking_holds WHERE status='held' AND expires_at <= UTC_TIMESTAMP()")
                cursor.execute(
                    "INSERT INTO phoenix_booking_holds (hold_token, practitioner_id, service_key, slot_utc, expires_at, status) "
                    "VALUES (%s,%s,%s,%s,DATE_ADD(UTC_TIMESTAMP(), INTERVAL 15 MINUTE),'held')",
                    (order_id, practitioner_id, service_key, _format_utc_slot(parsed_slot)),
                )
                conn.commit()
                return jsonify({
                    'order_id': order_id, 'approval_url': approval_url,
                    'charged_cents': charged_cents, 'practitioner_name': practitioner_name,
                })
            except Exception as exc:
                conn.rollback()
                return jsonify({'error': str(exc)}), 500
            finally:
                cursor.close(); conn.close()

        # Legacy / existing booking services continue to use the original PayPal flow.
        charged_cents = max(0, price_cents - (7500 if ffs_applied else 0))
        if esoteric_token:
            sep = '&' if '?' in return_url else '?'
            return_url = f"{return_url}{sep}esoteric_token={esoteric_token}"
        try:
            order_id, approval_url = paypal_create_order(
                charged_cents, f"Phoenix Rebirth | {service_name}", return_url, cancel_url
            )
            return jsonify({'order_id': order_id, 'approval_url': approval_url, 'charged_cents': charged_cents})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500


    @app.route('/paypal/capture-order', methods=['POST'])
    def paypal_capture():
        data = request.get_json(force=True, silent=True) or {}
        required = ['order_id','client_name','client_email','service_name','service_price_cents','charged_price_cents']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 400

        order_id = data['order_id']
        service_key = str(data.get('service_key', '')).strip()
        svc = _service(service_key) if service_key else None
        practitioner_id = int(data.get('practitioner_id', 0) or 0)
        practitioner_name = data.get('practitioner_name')

        price_cents = int(data['service_price_cents'])
        charged_cents = int(data['charged_price_cents'])
        expected_charged = max(0, price_cents - (7500 if data.get('ffs_credit_applied') else 0))
        if charged_cents != expected_charged:
            return jsonify({'error': 'Charged amount mismatch.'}), 400

        # Existing services remain on the legacy capture path. Practitioner-aware
        # services must have the complete practitioner/service data.
        if service_key and (not svc or not practitioner_id):
            return jsonify({'error': 'Practitioner booking information is missing or invalid.'}), 400
        if svc and price_cents != svc['price_cents']:
            return jsonify({'error': 'Service price mismatch.'}), 400

        slot_utc = data.get('slot_utc')
        if svc and not slot_utc:
            return jsonify({'error': 'A booking time is required.'}), 400

        # Legacy capture path: preserve the existing behavior for services that
        # are not practitioner-bookable.
        if not svc:
            try:
                capture_id = paypal_capture_order(order_id)
            except Exception as exc:
                return jsonify({'error': f'PayPal capture failed: {str(exc)}'}), 502

            gcal_event_id = None; meet_link = None
            if slot_utc:
                try:
                    duration = int(data.get('service_duration_minutes', 60))
                    gcal_event_id, meet_link = create_calendar_event(
                        slot_utc, duration,
                        f"Phoenix Rebirth | {data['service_name']} — {data['client_name']}",
                        f"Client: {data['client_name']}\nEmail: {data['client_email']}\nService: {data['service_name']}",
                        data['client_email'],
                    )
                except Exception:
                    pass

            try:
                booking_id = save_booking({
                    'client_name': data['client_name'], 'client_email': data['client_email'],
                    'service_name': data['service_name'], 'service_price_cents': price_cents,
                    'charged_price_cents': charged_cents, 'ffs_credit_applied': bool(data.get('ffs_credit_applied')),
                    'slot_utc': slot_utc, 'slot_mt': data.get('slot_mt'),
                    'client_timezone': data.get('client_timezone'), 'slot_client_display': data.get('slot_client_display'),
                    'slot_mt_display': data.get('slot_mt_display'), 'status': 'confirmed',
                    'paypal_order_id': order_id, 'paypal_capture_id': capture_id,
                    'google_calendar_event_id': gcal_event_id, 'google_meet_link': meet_link,
                    'confirmation_email_sent': False, 'practitioner_id': None,
                    'practitioner_name': None, 'service_key': None,
                })
            except Exception as exc:
                return jsonify({'error': f'Booking save failed: {str(exc)}'}), 500

            try:
                send_confirmation_email(data['client_email'], data['client_name'], data['service_name'], data.get('slot_mt_display') or 'Time TBD', meet_link)
            except Exception:
                pass

            if data.get('esoteric_token'):
                try:
                    conn = _get_db(); cursor = conn.cursor()
                    cursor.execute("UPDATE esoteric_requests SET token_used=1, updated_at=NOW() WHERE approval_token=%s", (data['esoteric_token'],))
                    conn.commit(); cursor.close(); conn.close()
                except Exception:
                    pass

            return jsonify({'status':'confirmed','booking_id':booking_id,'meet_link':meet_link,'order_id':order_id})

        conn = _get_db(); cursor = conn.cursor()
        try:
            hold = None
            cursor.execute(
                "SELECT practitioner_id, service_key, slot_utc, expires_at FROM phoenix_booking_holds "
                "WHERE hold_token=%s AND status='held' FOR UPDATE", (order_id,)
            )
            hold = cursor.fetchone()
            if not hold:
                return jsonify({'error': 'This PayPal booking session expired. Please choose the time again.'}), 409
            hold_pid, hold_key, hold_slot, expires_at = hold
            if int(hold_pid) != practitioner_id or hold_key != service_key:
                return jsonify({'error': 'Booking practitioner information does not match the reserved slot.'}), 409
            hold_slot_str = hold_slot.strftime('%Y-%m-%d %H:%M:%S') if hasattr(hold_slot, 'strftime') else str(hold_slot)
            requested_slot = _format_utc_slot(_parse_utc_slot(slot_utc)) if _parse_utc_slot(slot_utc) else ''
            if requested_slot != hold_slot_str:
                return jsonify({'error': 'Booking time does not match the reserved slot.'}), 409
            if not _practitioner_is_authorized(cursor, practitioner_id, service_key):
                return jsonify({'error': 'That practitioner is no longer authorized for this service.'}), 409

            cursor.execute(
                "SELECT 1 FROM bookings WHERE practitioner_id=%s AND slot_utc=%s "
                "AND status IN ('confirmed','pending_payment') LIMIT 1",
                (practitioner_id, hold_slot_str),
            )
            if cursor.fetchone():
                return jsonify({'error': 'That practitioner slot has already been booked.'}), 409

            # Capture only after the slot hold has been verified.
            try:
                capture_id = paypal_capture_order(order_id)
            except Exception as exc:
                return jsonify({'error': f'PayPal capture failed: {str(exc)}'}), 502

            duration = svc['duration_minutes'] + svc['buffer_minutes']
            gcal_event_id = None; meet_link = None
            try:
                gcal_event_id, meet_link = create_calendar_event(
                    hold_slot_str, duration,
                    f"Phoenix Rebirth | {data['service_name']} — {data['client_name']}",
                    f"Client: {data['client_name']}\nEmail: {data['client_email']}\nService: {data['service_name']}\nPractitioner: {practitioner_name or ''}",
                    data['client_email'],
                )
            except Exception:
                pass

            booking_row = {
                'client_name': data['client_name'], 'client_email': data['client_email'],
                'service_name': data['service_name'], 'service_price_cents': price_cents,
                'charged_price_cents': charged_cents, 'ffs_credit_applied': bool(data.get('ffs_credit_applied')),
                'slot_utc': hold_slot_str, 'slot_mt': data.get('slot_mt'),
                'client_timezone': data.get('client_timezone'), 'slot_client_display': data.get('slot_client_display'),
                'slot_mt_display': data.get('slot_mt_display'), 'status': 'confirmed',
                'paypal_order_id': order_id, 'paypal_capture_id': capture_id,
                'google_calendar_event_id': gcal_event_id, 'google_meet_link': meet_link,
                'confirmation_email_sent': False, 'practitioner_id': practitioner_id,
                'practitioner_name': practitioner_name or _practitioner_is_authorized(cursor, practitioner_id, service_key),
                'service_key': service_key,
            }
            cursor.execute(
                "INSERT INTO bookings (client_name,client_email,service_name,service_price_cents,charged_price_cents,ffs_credit_applied,"
                "slot_utc,slot_mt,client_timezone,slot_client_display,slot_mt_display,status,paypal_order_id,paypal_capture_id,"
                "google_calendar_event_id,google_meet_link,confirmation_email_sent,practitioner_id,practitioner_name,service_key) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (booking_row['client_name'],booking_row['client_email'],booking_row['service_name'],booking_row['service_price_cents'],
                 booking_row['charged_price_cents'],1 if booking_row['ffs_credit_applied'] else 0,booking_row['slot_utc'],booking_row['slot_mt'],
                 booking_row['client_timezone'],booking_row['slot_client_display'],booking_row['slot_mt_display'],booking_row['status'],
                 booking_row['paypal_order_id'],booking_row['paypal_capture_id'],booking_row['google_calendar_event_id'],
                 booking_row['google_meet_link'],0,booking_row['practitioner_id'],booking_row['practitioner_name'],booking_row['service_key'])
            )
            booking_id = cursor.lastrowid
            cursor.execute("DELETE FROM phoenix_booking_holds WHERE hold_token=%s", (order_id,))
            conn.commit()
        except Exception as exc:
            conn.rollback()
            return jsonify({'error': f'Booking save failed: {str(exc)}'}), 500
        finally:
            cursor.close(); conn.close()

        try:
            send_confirmation_email(
                data['client_email'], data['client_name'], data['service_name'],
                data.get('slot_mt_display') or 'Time TBD', meet_link,
                practitioner_name=practitioner_name or '',
            )
        except Exception:
            pass

        esoteric_token = data.get('esoteric_token', '')
        if esoteric_token:
            try:
                conn = _get_db(); cursor = conn.cursor()
                cursor.execute("UPDATE esoteric_requests SET token_used=1, updated_at=NOW() WHERE approval_token=%s", (esoteric_token,))
                conn.commit(); cursor.close(); conn.close()
            except Exception:
                pass

        return jsonify({'status':'confirmed','booking_id':booking_id,'meet_link':meet_link,'order_id':order_id})
