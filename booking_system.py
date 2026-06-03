"""
Phoenix Rebirth | soulReady — Booking System
Railway API endpoints for:
  POST /slots              — available time slots for a given month
  POST /paypal/create-order — create PayPal order, return approval URL
  POST /paypal/capture-order — capture payment, save booking, fire Google Calendar

Requires Railway environment variables:
  MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
  PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE (sandbox | live)
  GOOGLE_SERVICE_ACCOUNT_JSON   (full JSON string of service account credentials)
  GOOGLE_CALENDAR_ID            (christina@phoenixrebirth.life)
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS   (for confirmation emails)
"""

import json
import os
import smtplib
from datetime import datetime, timedelta, timezone, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
# Slot generation
# ---------------------------------------------------------------------------

MT_ZONE = ZoneInfo('America/Denver')
VALID_WEEKDAYS = {1, 2, 4, 5}   # Mon Tue Thu Fri (weekday() returns 0=Mon … 6=Sun)
SLOT_DURATION_MINUTES = 60
SLOT_INTERVAL_MINUTES = 60


def _get_schedule(cursor):
    """Load active schedule rows keyed by day_of_week (0=Sun … 6=Sat, MySQL convention)."""
    cursor.execute(
        "SELECT day_of_week, start_time, end_time FROM availability_schedule WHERE is_active = 1"
    )
    schedule = {}
    for row in cursor.fetchall():
        dow, start, end = row
        schedule[int(dow)] = {
            'start': (int(start.seconds // 3600), int((start.seconds % 3600) // 60)),
            'end':   (int(end.seconds // 3600),   int((end.seconds % 3600) // 60)),
        }
    return schedule


def _get_blocks(cursor, year, month):
    """Load blocked dates for the given month."""
    cursor.execute(
        "SELECT block_date FROM availability_blocks "
        "WHERE YEAR(block_date) = %s AND MONTH(block_date) = %s",
        (year, month),
    )
    return {row[0] for row in cursor.fetchall()}


def _get_booked_slots(cursor, year, month):
    """Return set of UTC datetime strings already booked (confirmed or pending_payment)."""
    cursor.execute(
        "SELECT slot_utc FROM bookings "
        "WHERE YEAR(slot_utc) = %s AND MONTH(slot_utc) = %s "
        "  AND status IN ('confirmed', 'pending_payment')",
        (year, month),
    )
    return {row[0] for row in cursor.fetchall() if row[0]}


def _mysql_weekday_to_python(mysql_dow):
    """MySQL: 0=Sun … 6=Sat. Python: 0=Mon … 6=Sun."""
    return (mysql_dow - 1) % 7


def generate_slots_for_month(year, month):
    """Return list of available slot dicts for the given month."""
    conn = _get_db()
    try:
        cursor = conn.cursor()
        schedule   = _get_schedule(cursor)
        blocked    = _get_blocks(cursor, year, month)
        booked_utc = _get_booked_slots(cursor, year, month)
        cursor.close()
    finally:
        conn.close()

    now_mt = datetime.now(MT_ZONE)
    slots  = []

    # Iterate every day of the month
    d = date(year, month, 1)
    while d.month == month:
        # MySQL day_of_week: 1=Mon … 7=Sun stored as 0=Sun 1=Mon
        # We stored Mon=1 Tue=2 Thu=4 Fri=5 in availability_schedule
        py_dow = d.weekday()  # 0=Mon
        mysql_dow = (py_dow + 1) % 7  # 0=Sun 1=Mon 2=Tue...

        if mysql_dow in schedule and d not in blocked:
            sched = schedule[mysql_dow]
            sh, sm = sched['start']
            eh, em = sched['end']
            slot_dt = datetime(year, d.month, d.day, sh, sm, tzinfo=MT_ZONE)
            end_dt  = datetime(year, d.month, d.day, eh, em, tzinfo=MT_ZONE)

            while slot_dt + timedelta(minutes=SLOT_DURATION_MINUTES) <= end_dt:
                # Skip slots in the past (with 1-hour buffer)
                if slot_dt > now_mt + timedelta(hours=1):
                    utc_dt = slot_dt.astimezone(timezone.utc)
                    utc_str = utc_dt.strftime('%Y-%m-%d %H:%M:%S')
                    if utc_str not in booked_utc:
                        slots.append({
                            'utc':      utc_str,
                            'mt':       slot_dt.strftime('%Y-%m-%d %H:%M'),
                            'label':    slot_dt.strftime('%-I:%M %p MT'),
                            'date':     d.isoformat(),
                            'weekday':  d.strftime('%A'),
                        })
                slot_dt += timedelta(minutes=SLOT_INTERVAL_MINUTES)

        d += timedelta(days=1)

    return slots


# ---------------------------------------------------------------------------
# PayPal helpers
# ---------------------------------------------------------------------------

def _paypal_base():
    mode = os.environ.get('PAYPAL_MODE', 'live')
    if mode == 'sandbox':
        return 'https://api-m.sandbox.paypal.com'
    return 'https://api-m.paypal.com'


def _paypal_token():
    resp = requests.post(
        f"{_paypal_base()}/v1/oauth2/token",
        auth=(os.environ['PAYPAL_CLIENT_ID'], os.environ['PAYPAL_CLIENT_SECRET']),
        data={'grant_type': 'client_credentials'},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def paypal_create_order(amount_cents, description, return_url, cancel_url):
    token   = _paypal_token()
    amount  = f"{amount_cents / 100:.2f}"
    payload = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'amount':      {'currency_code': 'USD', 'value': amount},
            'description': description,
        }],
        'application_context': {
            'return_url':       return_url,
            'cancel_url':       cancel_url,
            'shipping_preference': 'NO_SHIPPING',
            'user_action':         'PAY_NOW',
        },
    }
    resp = requests.post(
        f"{_paypal_base()}/v2/checkout/orders",
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    data         = resp.json()
    order_id     = data['id']
    approval_url = next(
        (link['href'] for link in data.get('links', []) if link['rel'] == 'approve'),
        None,
    )
    return order_id, approval_url


def paypal_capture_order(order_id):
    token = _paypal_token()
    resp  = requests.post(
        f"{_paypal_base()}/v2/checkout/orders/{order_id}/capture",
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=15,
    )
    resp.raise_for_status()
    data       = resp.json()
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

    info  = json.loads(sa_json)
    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=['https://www.googleapis.com/auth/calendar'],
    )
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)


def create_calendar_event(slot_utc_str, duration_minutes, summary, description, attendee_email):
    """Create a Google Calendar event and return (event_id, meet_link)."""
    service     = _gcal_service()
    calendar_id = os.environ.get('GOOGLE_CALENDAR_ID', 'christina@phoenixrebirth.life')

    start_dt = datetime.strptime(slot_utc_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    end_dt   = start_dt + timedelta(minutes=duration_minutes)

    event = {
        'summary':     summary,
        'description': description,
        'start':       {'dateTime': start_dt.isoformat(), 'timeZone': 'UTC'},
        'end':         {'dateTime': end_dt.isoformat(),   'timeZone': 'UTC'},
        'attendees':   [{'email': attendee_email}],
        'conferenceData': {
            'createRequest': {
                'requestId':             f"phoenix-{start_dt.timestamp():.0f}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        },
    }

    result   = service.events().insert(
        calendarId=calendar_id,
        body=event,
        conferenceDataVersion=1,
        sendUpdates='all',
    ).execute()

    event_id  = result.get('id')
    meet_link = result.get('hangoutLink')
    return event_id, meet_link


# ---------------------------------------------------------------------------
# Email confirmation
# ---------------------------------------------------------------------------

def send_confirmation_email(to_email, client_name, service_name, slot_mt_display, meet_link):
    host     = os.environ.get('SMTP_HOST')
    port     = int(os.environ.get('SMTP_PORT', 587))
    user     = os.environ.get('SMTP_USER')
    password = os.environ.get('SMTP_PASS')
    if not all([host, user, password]):
        return   # email not configured — skip silently

    msg            = MIMEMultipart('alternative')
    msg['Subject'] = f"Your session is confirmed — {service_name}"
    msg['From']    = f"Phoenix Rebirth <{user}>"
    msg['To']      = to_email

    meet_line = f"<p><strong>Google Meet:</strong> <a href='{meet_link}'>{meet_link}</a></p>" if meet_link else ''
    html = f"""
    <div style="font-family:Georgia,serif;color:#1a0a2e;max-width:600px;margin:0 auto;">
      <div style="background:#1a0a2e;padding:32px 40px;">
        <p style="font-family:'Georgia',serif;color:#d4af37;letter-spacing:4px;font-size:13px;text-transform:uppercase;margin:0;">
          Phoenix Rebirth | soulReady
        </p>
      </div>
      <div style="padding:40px;background:#fff;">
        <h2 style="color:#1a0a2e;font-size:22px;margin-top:0;">Your session is confirmed, {client_name}.</h2>
        <p><strong>Service:</strong> {service_name}</p>
        <p><strong>Time:</strong> {slot_mt_display}</p>
        {meet_line}
        <p style="margin-top:32px;color:#555;font-size:14px;">
          All sessions are conducted remotely. Your Google Meet link above is your virtual session room.
          Christina will be there at the scheduled time.
        </p>
        <p style="color:#555;font-size:14px;">
          Questions? Reply to this email or reach Christina at
          <a href="mailto:christina@phoenixrebirth.life">christina@phoenixrebirth.life</a>
        </p>
      </div>
      <div style="background:#f5f0ff;padding:20px 40px;">
        <p style="font-size:12px;color:#888;margin:0;">
          Phoenix Rebirth &bull; Christina Stevens &bull; Hobbs, NM &bull; Remote Worldwide
        </p>
      </div>
    </div>
    """

    msg.attach(MIMEText(html, 'html'))
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to_email, msg.as_string())


# ---------------------------------------------------------------------------
# Booking DB write
# ---------------------------------------------------------------------------

def save_booking(booking_data):
    conn   = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bookings (
                client_name, client_email, service_name, service_price_cents,
                charged_price_cents, ffs_credit_applied, slot_utc, slot_mt,
                client_timezone, slot_client_display, slot_mt_display,
                status, paypal_order_id, paypal_capture_id,
                google_calendar_event_id, google_meet_link, confirmation_email_sent
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
        """, (
            booking_data['client_name'],
            booking_data['client_email'],
            booking_data['service_name'],
            booking_data['service_price_cents'],
            booking_data['charged_price_cents'],
            1 if booking_data.get('ffs_credit_applied') else 0,
            booking_data.get('slot_utc'),
            booking_data.get('slot_mt'),
            booking_data.get('client_timezone'),
            booking_data.get('slot_client_display'),
            booking_data.get('slot_mt_display'),
            booking_data.get('status', 'confirmed'),
            booking_data.get('paypal_order_id'),
            booking_data.get('paypal_capture_id'),
            booking_data.get('google_calendar_event_id'),
            booking_data.get('google_meet_link'),
            1 if booking_data.get('confirmation_email_sent') else 0,
        ))
        conn.commit()
        booking_id = cursor.lastrowid
        return booking_id
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def check_ffs_credit(client_email):
    """Return True if client has an unused FFS credit."""
    conn   = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM bookings "
            "WHERE client_email = %s AND service_name = 'Field Frequency Scan' "
            "  AND status = 'confirmed' AND ffs_credit_applied = 0",
            (client_email,)
        )
        row = cursor.fetchone()
        return row[0] > 0
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

def register_booking_routes(app):

    @app.route('/slots', methods=['POST'])
    def slots():
        """
        POST body: {"year": 2026, "month": 6}
        Returns: {"slots": [...]}
        """
        data  = request.get_json(force=True, silent=True) or {}
        year  = data.get('year')
        month = data.get('month')
        if not year or not month:
            return jsonify({'error': 'year and month are required'}), 400
        try:
            available = generate_slots_for_month(int(year), int(month))
            return jsonify({'slots': available})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500


    @app.route('/ffs-credit', methods=['POST'])
    def ffs_credit():
        """
        POST body: {"email": "client@example.com"}
        Returns: {"hasCredit": true/false}
        """
        data  = request.get_json(force=True, silent=True) or {}
        email = data.get('email', '').strip().lower()
        if not email:
            return jsonify({'error': 'email is required'}), 400
        try:
            return jsonify({'hasCredit': check_ffs_credit(email)})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500


    @app.route('/paypal/create-order', methods=['POST'])
    def paypal_create():
        """
        POST body:
        {
          "service_name": "Guidance Session",
          "service_price_cents": 45000,
          "ffs_credit_applied": false,
          "return_url": "https://yourdomain.com/booking/success",
          "cancel_url": "https://yourdomain.com/booking/cancel"
        }
        Returns: {"order_id": "...", "approval_url": "..."}
        """
        data            = request.get_json(force=True, silent=True) or {}
        service_name    = data.get('service_name', '')
        price_cents     = int(data.get('service_price_cents', 0))
        ffs_applied     = bool(data.get('ffs_credit_applied', False))
        return_url      = data.get('return_url')
        cancel_url      = data.get('cancel_url')

        if not service_name or not price_cents or not return_url or not cancel_url:
            return jsonify({'error': 'service_name, service_price_cents, return_url, cancel_url are required'}), 400

        charged_cents = max(0, price_cents - (7500 if ffs_applied else 0))

        try:
            order_id, approval_url = paypal_create_order(
                charged_cents,
                f"Phoenix Rebirth | {service_name}",
                return_url,
                cancel_url,
            )
            return jsonify({
                'order_id':     order_id,
                'approval_url': approval_url,
                'charged_cents': charged_cents,
            })
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500


    @app.route('/paypal/capture-order', methods=['POST'])
    def paypal_capture():
        """
        POST body:
        {
          "order_id": "PAYPAL_ORDER_ID",
          "client_name": "Jane Smith",
          "client_email": "jane@example.com",
          "service_name": "Guidance Session",
          "service_price_cents": 45000,
          "charged_price_cents": 45000,
          "ffs_credit_applied": false,
          "slot_utc": "2026-06-10 14:00:00",
          "slot_mt": "2026-06-10 08:00",
          "client_timezone": "America/New_York",
          "slot_client_display": "Tuesday, June 10 at 10:00 AM ET",
          "slot_mt_display": "Tuesday, June 10 at 8:00 AM MT",
          "service_duration_minutes": 60
        }
        Returns: {"booking_id": "...", "meet_link": "...", "status": "confirmed"}
        """
        data = request.get_json(force=True, silent=True) or {}

        required = ['order_id', 'client_name', 'client_email', 'service_name',
                    'service_price_cents', 'charged_price_cents']
        missing  = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({'error': f"Missing fields: {', '.join(missing)}"}), 400

        order_id          = data['order_id']
        client_name       = data['client_name']
        client_email      = data['client_email']
        service_name      = data['service_name']
        price_cents       = int(data['service_price_cents'])
        charged_cents     = int(data['charged_price_cents'])
        ffs_applied       = bool(data.get('ffs_credit_applied', False))
        slot_utc          = data.get('slot_utc')
        slot_mt           = data.get('slot_mt')
        client_timezone   = data.get('client_timezone')
        slot_client_disp  = data.get('slot_client_display')
        slot_mt_disp      = data.get('slot_mt_display')
        duration          = int(data.get('service_duration_minutes', 60))

        # 1. Capture PayPal payment
        try:
            capture_id = paypal_capture_order(order_id)
        except Exception as exc:
            return jsonify({'error': f"PayPal capture failed: {str(exc)}"}), 502

        # 2. Google Calendar event (if slot provided)
        gcal_event_id = None
        meet_link     = None
        if slot_utc:
            try:
                gcal_event_id, meet_link = create_calendar_event(
                    slot_utc,
                    duration,
                    f"Phoenix Rebirth | {service_name} — {client_name}",
                    f"Client: {client_name}\nEmail: {client_email}\nService: {service_name}",
                    client_email,
                )
            except Exception:
                pass   # Calendar failure does not block the booking

        # 3. Save booking to MySQL
        try:
            booking_row = {
                'client_name':              client_name,
                'client_email':             client_email,
                'service_name':             service_name,
                'service_price_cents':      price_cents,
                'charged_price_cents':      charged_cents,
                'ffs_credit_applied':       ffs_applied,
                'slot_utc':                 slot_utc,
                'slot_mt':                  slot_mt,
                'client_timezone':          client_timezone,
                'slot_client_display':      slot_client_disp,
                'slot_mt_display':          slot_mt_disp,
                'status':                   'confirmed',
                'paypal_order_id':          order_id,
                'paypal_capture_id':        capture_id,
                'google_calendar_event_id': gcal_event_id,
                'google_meet_link':         meet_link,
                'confirmation_email_sent':  False,
            }
            save_booking(booking_row)
        except Exception as exc:
            return jsonify({'error': f"Booking save failed: {str(exc)}"}), 500

        # 4. Confirmation email
        try:
            send_confirmation_email(
                client_email, client_name, service_name,
                slot_mt_disp or 'Time TBD', meet_link,
            )
        except Exception:
            pass   # Email failure does not block response

        return jsonify({
            'status':    'confirmed',
            'meet_link': meet_link,
            'order_id':  order_id,
        })
