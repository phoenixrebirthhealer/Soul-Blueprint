import argparse
import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
import urllib.request
import urllib.error
from datetime import datetime as _datetime

from astrology_humandesign import (
    human_design_chart,
    human_design_chart_from_intake,
    set_ephemeris_path,
)
from sabian_symbols import get_sabian_for_chart
from transit_tracker import calculate_transit_map, parse_natal_points_from_api
from booking_system import (
    generate_slots_for_month,
    paypal_create_order,
    paypal_capture_order,
    create_calendar_event,
    send_confirmation_email,
    save_booking,
    check_ffs_credit,
)


CORS_HEADERS = [
    ("Access-Control-Allow-Origin", "*"),
    ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
    ("Access-Control-Allow-Headers", "Content-Type, Authorization"),
]

TEMPLATE_ROUTES = {
    "/hebrew-cube-template": "hebrew_metatron_cube_template.html",
    "/souls-journey-template": "souls_journey_template.html",
    "/ancestral-reading-template": "ancestral_reading_template.html",
    "/tcm-chakra-template": "tcm-chakra-wheel-template.html",
    "/name-frequency-template": "name_frequency_template.html",
    "/relational-tier1-template": "relational_tier1_template.html",
    "/relational-tier2-template": "relational_tier2_template.html",
    "/relational-tier3-template": "relational_tier3_template.html",
}

# In-memory job store for async server-side generation
_JOBS: Dict[str, Dict] = {}
_JOBS_LOCK = threading.Lock()


def _run_anthropic_generation(prompt: str, job_id: str) -> None:
    """Background thread: call Anthropic API and store result in job dict."""
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set on the server")

        payload = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read())

        result = data["content"][0]["text"]
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result": result}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


def _parse_time(time_str: str):
    """Parse time in 24-hour (HH:MM) or 12-hour (H:MM AM/PM) format. Returns (hour, minute)."""
    time_str = time_str.strip()
    is_pm = "PM" in time_str.upper()
    is_am = "AM" in time_str.upper()
    clean = time_str.upper().replace("AM", "").replace("PM", "").strip()
    parts = clean.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    if is_am and hour == 12:
        hour = 0
    elif is_pm and hour != 12:
        hour += 12
    return hour, minute


# ---------- Name Frequency Reading Generation ----------

_LETTER_VALUES = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,'J':10,
    'K':11,'L':12,'M':13,'N':14,'O':15,'P':16,'Q':17,'R':18,'S':19,'T':20,
    'U':21,'V':22,'W':23,'X':24,'Y':25,'Z':26,
}
_MASTER = {11, 22, 33}
_CHAKRA = {
    0:'Soul in Purest Form',1:'Root',2:'Sacral',3:'Solar Plexus',
    4:'Heart',5:'Throat',6:'Third Eye',7:'Crown',8:'Soul Star',9:'Earth Star',
    11:'Double Root',22:'Double Sacral',33:'Double Solar Plexus',
}

def _chakra_label(value: int) -> str:
    if value in _MASTER:
        return _CHAKRA[value]
    if value <= 9:
        return _CHAKRA.get(value, 'Soul in Purest Form')
    tens, ones = value // 10, value % 10
    return _CHAKRA.get(tens, 'Soul in Purest Form') + ' leads ' + _CHAKRA.get(ones, 'Soul in Purest Form')

def _calc_name_frequency(display_words: list) -> list:
    result = []
    for word in display_words:
        letters = []
        for ch in word.upper():
            if ch.isalpha():
                val = _LETTER_VALUES.get(ch, 0)
                letters.append({'letter': ch, 'value': val, 'chakraLabel': _chakra_label(val)})
        result.append({'word': word.upper(), 'letters': letters})
    return result

def _call_anthropic(prompt: str, max_tokens: int = 4096) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data["content"][0]["text"]

def _parse_json_response(raw) -> dict:
    try:
        txt = raw.strip() if isinstance(raw, str) else json.dumps(raw)
        if txt.startswith('`'):
            txt = txt.replace('```json', '').replace('```', '').strip()
        return json.loads(txt)
    except Exception:
        return {}

def _run_name_frequency_generation(client_name: str, display_words: list, job_id: str) -> None:
    try:
        nf_data = _calc_name_frequency(display_words)

        # Build position-aware letter list for full journey prompt
        letter_lines = []
        for wi, word in enumerate(nf_data):
            dw = display_words[wi]
            total = len(word['letters'])
            for li, l in enumerate(word['letters']):
                if li == 0:
                    pos = 'OPENS'
                elif li == total - 1:
                    pos = 'CLOSES'
                else:
                    pos = f'position {li+1} of {total}'
                letter_lines.append(f"[{dw} / {pos} / letter {l['letter']} / value {l['value']} / {l['chakraLabel']}]")
        letter_list = '\n'.join(letter_lines)

        all_letter_texts = []
        all_name_summaries = {}

        for wi, word in enumerate(nf_data):
            dw = display_words[wi]
            total = len(word['letters'])
            word_letter_list = []
            for li, l in enumerate(word['letters']):
                if li == 0:
                    pos = 'OPENS'
                elif li == total - 1:
                    pos = 'CLOSES'
                else:
                    pos = f'position {li+1} of {total}'
                word_letter_list.append(f"[{dw} / {pos} / letter {l['letter']} / value {l['value']} / {l['chakraLabel']}]")

            placeholder = ',"4+ sentences"' * (total - 1)
            prompt = f"""You are writing a Name Frequency Reading for one name: {dw}, part of the full name {client_name}. Voice of Christina Stevens, Phoenix Rebirth.

CRITICAL RULES:
The chakra label for each letter is PRE-CALCULATED below. Write every description locked to that exact label only.
If the label says "Root leads Heart" write about Root leads Heart. Both energies. In that order.
NEVER reference any chakra not in the pre-calculated label.
NEVER use em dashes. NEVER use the word medicine, use Rebirth. Master numbers 11, 22, 33 are NEVER reduced.

CHAKRA KEY:
Root = foundation, grounding, physical presence, core identity
Sacral = creative energy, generative force, life force expression
Solar Plexus = personal power, will, confidence, the fire of self
Heart = love, connection, giving and receiving
Throat = authentic voice, expression, truth in sound
Third Eye = intuition, inner vision, expanded perception
Crown = divine connection, higher consciousness, the infinite
Soul Star = soul mission, frequency beyond this lifetime
Earth Star = physical embodiment, grounded manifestation
Soul in Purest Form = the zero point, frequency before identity forms

When a label says "X leads Y" address both energies in that order. X first. Y second.

VOICE:
Direct, warm, fierce, unfiltered. Every sentence specific to THIS letter at THIS position in THIS name. Plain language. Make this person feel SEEN not informed.

LETTERS FOR {dw.upper()}:
{chr(10).join(word_letter_list)}

POSITION MEANINGS:
OPENS = what this name activates first in the world
CLOSES = what this person carries forward from this name
Middle = interior architecture, working material within this name

FOR EACH LETTER write minimum 4 sentences:
1. What this chakra frequency has been doing in this person's life. A recognition, not a definition.
2. What it means this frequency sits at OPENS, CLOSES, or this middle position.
3. What this frequency has been building in this soul's life.
4. What this frequency is asking them to trust now.

FOR NAME SUMMARY write minimum 4 sentences:
What is {dw} built to do as a soul instruction?

Return ONLY valid JSON:
{{"letterTexts":["4+ sentences"{placeholder}],"nameSummary":"4+ sentences"}}"""

            raw = _call_anthropic(prompt, max_tokens=4096)
            parsed = _parse_json_response(raw)
            texts = parsed.get('letterTexts', [])
            if not isinstance(texts, list):
                texts = []
            all_letter_texts.extend(texts)
            all_name_summaries[dw] = parsed.get('nameSummary', '')

        # Journey + love + closing
        journey_prompt = f"""You are writing closing sections of a Name Frequency Reading for {client_name}. Voice of Christina Stevens, Phoenix Rebirth.

RULES:
NEVER use em dashes. NEVER use the word medicine, use Rebirth. Master numbers 11, 22, 33 are NEVER reduced. Direct, warm, fierce voice. Every sentence specific to this person.

COMPLETE NAME LETTER DATA:
{letter_list}

FULL JOURNEY -- 4 paragraphs in HTML p tags:
How do all names work together as one soul arc? Name every repeating frequency and what it insists on. What does the full name reveal that no single name could show alone?

LOVE IN YOUR FREQUENCY -- 3 paragraphs in HTML p tags:
Only the chakra frequencies in this name that speak to how this soul gives and receives love. Close with a bridge toward the Self-Love Language Reading.

CLOSING LINE -- one line specific to this person only.

Return ONLY valid JSON:
{{"fullJourney":"<p>p1</p><p>p2</p><p>p3</p><p>p4</p>","loveSection":"<p>p1</p><p>p2</p><p>p3</p>","closing":"one line"}}"""

        raw_j = _call_anthropic(journey_prompt, max_tokens=4096)
        journey = _parse_json_response(raw_j)

        full_journey  = journey.get('fullJourney', '<p>Your name sequence is your soul map.</p>')
        love_section  = journey.get('loveSection', '<p>Your frequencies shape how love moves through you.</p>')
        closing       = journey.get('closing', 'Your name has always known who you are. Now you do too.')

        # Fetch and assemble HTML template
        template_path = Path(__file__).parent / "tcm-system" / "name_frequency_template.html"
        html = template_path.read_text(encoding="utf-8")

        all_nav_words = display_words + ['The Full Journey']
        num_sections  = len(display_words) + 1

        def dots(active_idx):
            return ''.join(
                f'<div class="dot{" active" if j == active_idx else ""}" onclick="showSection({j})"></div>'
                for j in range(num_sections)
            )

        letter_idx = 0
        name_sections_html = []
        for i, word in enumerate(nf_data):
            dw = display_words[i]
            eyebrow = 'First Name' if i == 0 else ('Last Name' if i == len(nf_data) - 1 else 'Middle Name')
            cards_html = []
            for l in word['letters']:
                text = all_letter_texts[letter_idx] if letter_idx < len(all_letter_texts) else f"{l['chakraLabel']} frequency activates here."
                letter_idx += 1
                tag_display = l['chakraLabel'].replace(' leads ', ' leads<br>') if ' leads ' in l['chakraLabel'] else l['chakraLabel']
                cards_html.append(f"""<div class="letter-card">
  <div class="letter-marker">
    <div class="letter-glyph">{l['letter']}</div>
    <div class="letter-num">{l['value']}</div>
    <div class="letter-chakra-tag">{tag_display}</div>
  </div>
  <div class="letter-content">
    <div class="chakra-label">{l['chakraLabel']}</div>
    <div class="letter-text">{text}</div>
  </div>
</div>""")

            summary_text = all_name_summaries.get(dw, '')
            summary_html = (f'<div class="name-summary"><div class="summary-label">{dw} as a Whole</div>'
                            f'<div class="summary-text">{summary_text}</div></div>') if summary_text else ''
            prev_btn = ('<button class="nav-arrow hidden">Back</button>' if i == 0
                        else f'<button class="nav-arrow" onclick="showSection({i-1})">&#8592; Back</button>')

            name_sections_html.append(f"""<div class="reading-section{' active' if i == 0 else ''}" id="section-{i}">
  <div class="section-header"><div class="section-eyebrow">{eyebrow}</div><h2>{dw}</h2><p class="tagline">The frequency encoded in this name.</p></div>
{''.join(cards_html)}
{summary_html}
  <div class="nav-bottom">{prev_btn}<div class="section-dots">{dots(i)}</div><button class="nav-arrow" onclick="showSection({i+1})">Next &#8594;</button></div>
</div>""")

        journey_idx = len(display_words)
        journey_section_html = f"""<div class="reading-section" id="section-{journey_idx}">
  <div class="section-header"><div class="section-eyebrow">The Complete Soul Journey</div><h2>{client_name}</h2><p class="tagline">The whole story in one arc.</p></div>
  <div class="integration"><div class="integration-title">The Full Soul Journey</div><div class="integration-text">{full_journey}</div></div>
  <div class="bridge"><div class="bridge-title">The Love in Your Frequency</div><div class="bridge-text">{love_section}</div></div>
  <div class="closing"><div class="closing-line">{closing}</div><div class="closing-attribution">Phoenix Rebirth | Name Frequency Reading | Christina Stevens</div></div>
  <div class="nav-bottom"><button class="nav-arrow" onclick="showSection({journey_idx-1})">&#8592; Back</button><div class="section-dots">{dots(journey_idx)}</div><button class="nav-arrow hidden">Next</button></div>
</div>"""

        nav_html = '\n    '.join(
            f'<button class="nav-btn{" active" if i == 0 else ""}" onclick="showSection({i})">{w}</button>'
            for i, w in enumerate(all_nav_words)
        )

        import re
        html = html.replace('<!--NAMFREQ_CLIENT_NAME-->', client_name)
        html = re.sub(r'<!--NAMFREQ_NAV_START-->[\s\S]*?<!--NAMFREQ_NAV_END-->',
                      f'<!--NAMFREQ_NAV_START-->\n    {nav_html}\n    <!--NAMFREQ_NAV_END-->', html)
        html = re.sub(r'<!--NAMFREQ_CONTENT_START-->[\s\S]*?<!--NAMFREQ_CONTENT_END-->',
                      f'<!--NAMFREQ_CONTENT_START-->\n{"".join(name_sections_html)}\n{journey_section_html}\n<!--NAMFREQ_CONTENT_END-->', html)
        html = html.replace('<!--NAMFREQ_FOOTER-->',
                            f'Phoenix Rebirth · Name Frequency Reading · {client_name} · Proprietary · 2026')

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result": html}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


class LocalAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code: int, content: str) -> None:
        body = content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path == "/health":
            self._send_json(200, {"status": "ok"})

        elif path in TEMPLATE_ROUTES:
            filename = TEMPLATE_ROUTES[path]
            try:
                template_path = Path(__file__).parent / "tcm-system" / filename
                content = template_path.read_text(encoding="utf-8")
                self._send_html(200, content)
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/template-check":
            base = Path(__file__).parent / "tcm-system"
            result = {}
            for route, fname in TEMPLATE_ROUTES.items():
                p = base / fname
                result[fname] = {"exists": p.exists(), "size": p.stat().st_size if p.exists() else 0}
            self._send_json(200, {"base_dir": str(base), "cwd": os.getcwd(), "files": result})

        elif path.startswith("/job-status/"):
            job_id = path[len("/job-status/"):]
            with _JOBS_LOCK:
                job = dict(_JOBS.get(job_id, {}))
            if not job:
                self._send_json(404, {"error": "job not found or already retrieved"})
                return
            self._send_json(200, job)
            if job.get("status") in ("complete", "failed"):
                with _JOBS_LOCK:
                    _JOBS.pop(job_id, None)

        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        body_bytes = self.rfile.read(content_length)
        body = body_bytes.decode("utf-8") if body_bytes else ""
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON body"})
            return

        path = self.path.split("?")[0]

        if path == "/chart":
            try:
                chart = self._build_chart(payload)
                self._send_json(200, chart)
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})

        elif path == "/generate-name-frequency":
            first  = payload.get("first_name", "").strip()
            middle = payload.get("middle_name", "").strip()
            last   = payload.get("last_name", "").strip()
            if not first or not last:
                self._send_json(400, {"error": "first_name and last_name are required"})
                return
            parts = [p for p in [first, middle, last] if p]
            client_name = " ".join(parts)
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(
                target=_run_name_frequency_generation,
                args=(client_name, parts, job_id),
                daemon=True,
            )
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/start-generation":
            prompt = payload.get("prompt", "")
            if not prompt:
                self._send_json(400, {"error": "'prompt' is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(
                target=_run_anthropic_generation,
                args=(prompt, job_id),
                daemon=True,
            )
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/sabian-symbols":
            try:
                # Accept { "planets": {...} } or the planet dict directly at top level
                planets = payload.get("planets") or {k: v for k, v in payload.items() if k != "planets"}
                if not planets:
                    self._send_json(200, {})
                    return
                results = get_sabian_for_chart(planets)
                self._send_json(200, results)
            except Exception as exc:
                self._send_json(200, {"error": str(exc)})

        elif path == "/transit-tracker":
            try:
                birth_date_str = payload.get("birth_date", "")
                rising_sign = payload.get("rising_sign", "")
                astrology_data = payload.get("astrology_data", {})
                months = int(payload.get("months", 36))
                if not birth_date_str or not rising_sign:
                    self._send_json(400, {"error": "birth_date and rising_sign are required"})
                    return
                birth_date = _datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                natal_points = parse_natal_points_from_api(astrology_data)
                if not natal_points:
                    self._send_json(400, {"error": "Could not parse any natal points from astrology_data"})
                    return
                result = calculate_transit_map(
                    birth_date=birth_date,
                    natal_points=natal_points,
                    rising_sign=rising_sign,
                    months=months,
                )
                self._send_json(200, result)
            except Exception as exc:
                self._send_json(200, {"error": str(exc)})

        elif path == "/slots":
            year  = payload.get("year")
            month = payload.get("month")
            if not year or not month:
                self._send_json(400, {"error": "year and month are required"})
                return
            try:
                available = generate_slots_for_month(int(year), int(month))
                self._send_json(200, {"slots": available})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/ffs-credit":
            email = payload.get("email", "").strip().lower()
            if not email:
                self._send_json(400, {"error": "email is required"})
                return
            try:
                self._send_json(200, {"hasCredit": check_ffs_credit(email)})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/paypal/create-order":
            service_name  = payload.get("service_name", "")
            price_cents   = int(payload.get("service_price_cents", 0))
            ffs_applied   = bool(payload.get("ffs_credit_applied", False))
            return_url    = payload.get("return_url")
            cancel_url    = payload.get("cancel_url")
            if not service_name or not price_cents or not return_url or not cancel_url:
                self._send_json(400, {"error": "service_name, service_price_cents, return_url, cancel_url are required"})
                return
            charged_cents = max(0, price_cents - (7500 if ffs_applied else 0))
            try:
                order_id, approval_url = paypal_create_order(
                    charged_cents,
                    f"Phoenix Rebirth | {service_name}",
                    return_url,
                    cancel_url,
                )
                self._send_json(200, {
                    "order_id":      order_id,
                    "approval_url":  approval_url,
                    "charged_cents": charged_cents,
                })
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/paypal/capture-order":
            required = ["order_id", "client_name", "client_email", "service_name",
                        "service_price_cents", "charged_price_cents"]
            missing  = [f for f in required if not payload.get(f)]
            if missing:
                self._send_json(400, {"error": f"Missing fields: {', '.join(missing)}"})
                return

            order_id         = payload["order_id"]
            client_name      = payload["client_name"]
            client_email     = payload["client_email"]
            service_name     = payload["service_name"]
            price_cents      = int(payload["service_price_cents"])
            charged_cents    = int(payload["charged_price_cents"])
            ffs_applied      = bool(payload.get("ffs_credit_applied", False))
            slot_utc         = payload.get("slot_utc")
            slot_mt          = payload.get("slot_mt")
            client_timezone  = payload.get("client_timezone")
            slot_client_disp = payload.get("slot_client_display")
            slot_mt_disp     = payload.get("slot_mt_display")
            duration         = int(payload.get("service_duration_minutes", 60))

            try:
                capture_id = paypal_capture_order(order_id)
            except Exception as exc:
                self._send_json(502, {"error": f"PayPal capture failed: {str(exc)}"})
                return

            gcal_event_id = None
            meet_link     = None
            if slot_utc:
                try:
                    gcal_event_id, meet_link = create_calendar_event(
                        slot_utc, duration,
                        f"Phoenix Rebirth | {service_name} — {client_name}",
                        f"Client: {client_name}\nEmail: {client_email}\nService: {service_name}",
                        client_email,
                    )
                except Exception:
                    pass

            try:
                save_booking({
                    "client_name":              client_name,
                    "client_email":             client_email,
                    "service_name":             service_name,
                    "service_price_cents":      price_cents,
                    "charged_price_cents":      charged_cents,
                    "ffs_credit_applied":       ffs_applied,
                    "slot_utc":                 slot_utc,
                    "slot_mt":                  slot_mt,
                    "client_timezone":          client_timezone,
                    "slot_client_display":      slot_client_disp,
                    "slot_mt_display":          slot_mt_disp,
                    "status":                   "confirmed",
                    "paypal_order_id":          order_id,
                    "paypal_capture_id":        capture_id,
                    "google_calendar_event_id": gcal_event_id,
                    "google_meet_link":         meet_link,
                    "confirmation_email_sent":  False,
                })
            except Exception as exc:
                self._send_json(500, {"error": f"Booking save failed: {str(exc)}"})
                return

            try:
                send_confirmation_email(
                    client_email, client_name, service_name,
                    slot_mt_disp or "Time TBD", meet_link,
                )
            except Exception:
                pass

            self._send_json(200, {
                "status":    "confirmed",
                "meet_link": meet_link,
                "order_id":  order_id,
            })

        else:
            self._send_json(404, {"error": "endpoint not found"})

    def _build_chart(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        date = payload.get("date")
        time = payload.get("time")
        if not date or not time:
            raise ValueError("'date' and 'time' are required")

        sep = "/" if "/" in date else "-"
        parts = [int(p) for p in date.split(sep)]
        if parts[0] > 31:
            year, month, day = parts[0], parts[1], parts[2]
        else:
            month, day, year = parts[0], parts[1], parts[2]
        hour, minute = _parse_time(time)

        timezone_name = payload.get("timezone")
        timezone_offset = payload.get("timezoneOffset")
        location = payload.get("location")
        latitude = payload.get("latitude")
        longitude = payload.get("longitude")
        country_hint = payload.get("countryHint")

        if timezone_name is not None:
            tz_value = timezone_name
        elif timezone_offset is not None:
            tz_value = str(timezone_offset)
        else:
            tz_value = None

        if latitude is not None and longitude is not None:
            chart = human_design_chart(
                year,
                month,
                day,
                hour,
                minute,
                float(latitude),
                float(longitude),
                tz_value,
                88,
            )
        elif location:
            chart = human_design_chart_from_intake(
                year,
                month,
                day,
                hour,
                minute,
                location,
                timezone_offset=timezone_offset,
                timezone_name=timezone_name,
                country_hint=country_hint,
                design_offset_days=88,
            )
        else:
            raise ValueError("Either 'location' or both 'latitude' and 'longitude' must be provided")

        chart = self._inject_retrograde(chart, year, month, day, hour, minute, tz_value)
        return chart

    def _inject_retrograde(self, chart, year, month, day, hour, minute, tz_value) -> Dict[str, Any]:
        try:
            import swisseph as swe
            from datetime import datetime

            offset_hours = 0
            if tz_value is not None:
                try:
                    offset_hours = float(tz_value)
                except ValueError:
                    try:
                        import pytz
                        tz = pytz.timezone(tz_value)
                        dt = datetime(year, month, day, hour, minute)
                        offset_hours = tz.utcoffset(dt).total_seconds() / 3600
                    except Exception:
                        offset_hours = 0

            ut_hour = hour - offset_hours + minute / 60.0
            jd = swe.julday(year, month, day, ut_hour)

            planet_ids = {
                "sun": swe.SUN,
                "moon": swe.MOON,
                "mercury": swe.MERCURY,
                "venus": swe.VENUS,
                "mars": swe.MARS,
                "jupiter": swe.JUPITER,
                "saturn": swe.SATURN,
                "uranus": swe.URANUS,
                "neptune": swe.NEPTUNE,
                "pluto": swe.PLUTO,
                "chiron": swe.CHIRON,
            }

            retrograde_map = {}
            for name, pid in planet_ids.items():
                result, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
                speed = result[3]
                retrograde_map[name] = speed < 0

            if "birth" in chart and "planet_positions" in chart["birth"]:
                for p in chart["birth"]["planet_positions"]:
                    key = p["planet"].lower().replace(" ", "")
                    if key in retrograde_map:
                        p["retrograde"] = retrograde_map[key]

        except Exception:
            pass

        return chart

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server(port: int, ephe_path: Optional[str]) -> None:
    set_ephemeris_path(ephe_path)
    server = HTTPServer(("", port), LocalAPIHandler)
    print(f"Local API running on http://127.0.0.1:{port}")
    print("POST JSON to /chart; GET /health for status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping local API server...")
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a local astrology and Human Design API server.")
    parser.add_argument("--port", type=int, default=8000, help="Port for the local API server")
    parser.add_argument(
        "--ephe-path",
        required=False,
        default=None,
        help="Optional path to Swiss Ephemeris data files",
    )
    args = parser.parse_args()
    run_server(args.port, args.ephe_path)
