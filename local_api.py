import argparse
import json
import os
import re
import sys
import threading
import urllib.request
import uuid
from datetime import datetime as _datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

_JOBS: dict = {}
_JOBS_LOCK = threading.Lock()

print("local_api.py: starting imports", flush=True)
try:
    print("local_api.py: attempting imports", flush=True)
    from astrology_humandesign import (
        human_design_chart,
        human_design_chart_from_intake,
        set_ephemeris_path,
    )
    print("local_api.py: astrology_humandesign OK", flush=True)
except Exception as _import_exc:
    import traceback
    print(f"FATAL IMPORT ERROR: {_import_exc}", flush=True)
    traceback.print_exc()
    sys.exit(1)

CORS_HEADERS = [
    ("Access-Control-Allow-Origin", "*"),
    ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
    ("Access-Control-Allow-Headers", "Content-Type, Authorization"),
]

# ---------------------------------------------------------------------------
# Hebrew position reference data
# ---------------------------------------------------------------------------
_SB_HEB_POS_REF = {
    0:  {"name": "The Fool",  "element": "Void",  "meaning": "The sacred beginning. The soul before incarnation. Pure potential."},
    1:  {"name": "Aleph",    "element": "Air",   "meaning": "The breath of God. The first vibration. Silent power."},
    2:  {"name": "Bet",      "element": "Earth", "meaning": "The house. The container. Where spirit meets matter."},
    3:  {"name": "Gimel",    "element": "Fire",  "meaning": "The camel. Movement through the desert. Sustained journey."},
    4:  {"name": "Dalet",    "element": "Earth", "meaning": "The door. Threshold between worlds. Humility as gateway."},
    5:  {"name": "Heh",      "element": "Air",   "meaning": "The window. Divine breath. Revelation and seeing."},
    6:  {"name": "Vav",      "element": "Earth", "meaning": "The nail. Connection. The hook that joins heaven and earth."},
    7:  {"name": "Zayin",    "element": "Air",   "meaning": "The sword. Discernment. The cut that liberates."},
    8:  {"name": "Chet",     "element": "Water", "meaning": "The fence. Sacred enclosure. Life force protected."},
    9:  {"name": "Tet",      "element": "Earth", "meaning": "The serpent. Hidden goodness. Coiled wisdom rising."},
    10: {"name": "Yod",      "element": "Fire",  "meaning": "The hand of God. Divine spark. Smallest letter, infinite power."},
    11: {"name": "Kaf",      "element": "Fire",  "meaning": "The palm. Receptivity. Crowning and containment."},
    12: {"name": "Lamed",    "element": "Air",   "meaning": "The ox goad. Learning through experience. The heart's teacher."},
    13: {"name": "Mem",      "element": "Water", "meaning": "The waters. The womb of creation. Flowing transformation."},
    14: {"name": "Nun",      "element": "Water", "meaning": "The fish. Faithfulness in depth. Soul swimming in the unconscious."},
    15: {"name": "Samech",   "element": "Fire",  "meaning": "The support. Divine protection. The cycle that sustains."},
    16: {"name": "Ayin",     "element": "Earth", "meaning": "The eye. Perception. Seeing the divine in the material."},
    17: {"name": "Peh",      "element": "Air",   "meaning": "The mouth. Expression. Sacred speech that creates worlds."},
    18: {"name": "Tzadi",    "element": "Water", "meaning": "The fishhook. The righteous one. Pulling truth from depths."},
    19: {"name": "Qof",      "element": "Earth", "meaning": "The back of the head. The unconscious. Sacred cycles."},
    20: {"name": "Resh",     "element": "Air",   "meaning": "The head. Leadership of consciousness. Choosing the divine."},
    21: {"name": "Shin",     "element": "Fire",  "meaning": "The divine fire. Love. The letter with which God signed creation."},
    22: {"name": "Tav",      "element": "Earth", "meaning": "The mark. Completion. The seal of truth on all creation."},
}

_SB_VOICE_RULES = """
VOICE AND TONE RULES (NON-NEGOTIABLE):
- Write in second person (you/your) directly to the client
- Warm, reverent, soul-centered — never clinical or diagnostic
- This system is called Phoenix Rebirth Numerology / Hebrew Metatron's Cube
- Never use the word "medicine" — use "Rebirth" instead
- Never use disorder/condition/diagnosis — use "wiring pattern" or "soul design"
- Never use em dashes (—) anywhere
- Readings ACTIVATE Rebirths — they do not give advice
- Position 21 Shin is ALWAYS the first stop on the journey (convergence power point)
- Position 0 The Fool is ALWAYS the final stop (the return to wholeness)
- Status meanings: healed = fully integrated, bridge = in active integration, shadow = blocked/unprocessed, not_activated = no activation in this lifetime
""".strip()

_SB_CAREER_RULERSHIP = {
    "spiritual": "Neptune/Jupiter",
    "healing": "Neptune/Chiron",
    "coaching": "Jupiter/Saturn",
    "teaching": "Mercury/Jupiter",
    "creative": "Venus/Neptune",
    "business": "Saturn/Jupiter",
    "technology": "Uranus/Mercury",
    "leadership": "Sun/Saturn",
}

_SB_CAREER_EXPR = {
    "transformation": "depth work, shadow integration, soul alchemy",
    "healing": "energy clearing, somatic work, frequency restoration",
    "guide": "mentorship, way-showing, holding sacred space",
    "facilitator": "group containers, process work, community activation",
    "teacher": "curriculum, transmission, knowledge embodiment",
    "creator": "art, expression, beauty as spiritual practice",
}


def _sb_classify_statuses(
    questionnaire: list,
    l1_positions: list,
    l2_positions: list,
    fib_activations: list,
) -> dict:
    """Classify Hebrew position statuses from felt responses."""
    activated = set()
    for p in l1_positions:
        pos = int(p.get("position", -1))
        if pos >= 0:
            activated.add(pos)
    for p in l2_positions:
        pos = int(p.get("position", -1))
        if pos >= 0:
            activated.add(pos)

    statuses = {}
    felt_map = {}
    for r in questionnaire:
        pos = int(r.get("position", 0))
        felt = (r.get("feltResponse") or "").strip()
        if felt:
            felt_map[pos] = felt.lower()

    SHADOW_WORDS = ["sick", "nausea", "pain", "pressure", "heavy", "dread", "fear", "shame", "grief", "stuck", "blocked", "dark", "suffocate", "tight", "hollow", "numb", "rage", "anger", "lost"]
    HEALED_WORDS = ["peace", "love", "bliss", "calm", "serene", "joy", "free", "light", "open", "clear", "warm", "safe", "whole", "home", "radiant", "grace", "divine", "source", "presence", "power"]
    BRIDGE_WORDS = ["protective", "airy", "floaty", "resonance", "mist", "divinity", "blaze", "sunrise", "patience", "darkness", "depth", "temperance", "ego", "balance"]

    for pos in range(23):
        if pos not in activated:
            statuses[str(pos)] = "not_activated"
            continue
        felt = felt_map.get(pos, "")
        if not felt:
            statuses[str(pos)] = "not_activated"
            continue
        if any(w in felt for w in SHADOW_WORDS):
            statuses[str(pos)] = "shadow"
        elif any(w in felt for w in HEALED_WORDS):
            statuses[str(pos)] = "healed"
        elif any(w in felt for w in BRIDGE_WORDS):
            statuses[str(pos)] = "bridge"
        else:
            statuses[str(pos)] = "bridge"

    return statuses


def _sb_build_prompt(payload: dict) -> str:
    """Build the Soul Blueprint generation prompt."""
    client_d = payload.get("client", {})
    astro = payload.get("astrology", {})
    hd = payload.get("humanDesign", {})
    num = payload.get("numerology", {})
    heb = payload.get("hebrew", {})
    assess = payload.get("assessment", {})

    _l1_pos = set(int(p.get("position", -1)) for p in heb.get("layer1Positions", []) if p.get("position", -1) >= 0)
    _l2_pos = set(int(p.get("position", -1)) for p in heb.get("layer2Positions", []) if p.get("position", -1) >= 0)
    _activated_str = ", ".join(str(p) for p in sorted(_l1_pos | _l2_pos)) if (_l1_pos | _l2_pos) else "none"

    def p(key): return astro.get(key) or "not entered"

    statuses = heb.get("positionStatuses", {})
    q = assess.get("hebrewQuestionnaire", [])

    heb_lines = []
    for pos in sorted(_l1_pos | _l2_pos):
        ref = _SB_HEB_POS_REF.get(pos, {})
        status = statuses.get(str(pos), "not_activated")
        felt = next((r.get("feltResponse", "") for r in q if int(r.get("position", 0)) == pos), "")
        l1c = sum(1 for x in heb.get("layer1Positions", []) if int(x.get("position", -1)) == pos)
        l2c = sum(1 for x in heb.get("layer2Positions", []) if int(x.get("position", -1)) == pos)
        heb_lines.append(
            f"Position {pos} {ref.get('name','')}: element={ref.get('element','')}, "
            f"meaning={ref.get('meaning','')}, status={status}, "
            f"layer1_activations={l1c}, layer2_activations={l2c}, "
            f"felt_response={felt or 'none'}"
        )

    convergence = heb.get("convergencePoints", [])
    unique_convergence = list(dict.fromkeys(convergence))

    prompt = f"""
{_SB_VOICE_RULES}

You are generating a Soul Blueprint Decoder Tier 1 reading for:
Name: {client_d.get('firstName', '')} {client_d.get('middleName', '')} {client_d.get('lastName', '')}
Date of Birth: {client_d.get('dateOfBirth', '')}
Place of Birth: {client_d.get('placeOfBirth', '')}
Career Field: {client_d.get('careerField', '')}
Career Expression: {client_d.get('careerExpression', '')}

ASTROLOGY:
Rising: {p('rising')} | Chart Ruler: {p('chartRuler')} | Midheaven: {p('midheaven')}
Sun: {p('sun')} | Moon: {p('moon')} | Mercury: {p('mercury')}
Venus: {p('venus')} | Mars: {p('mars')} | Jupiter: {p('jupiter')}
Saturn: {p('saturn')} | Uranus: {p('uranus')} | Neptune: {p('neptune')}
Pluto: {p('pluto')} | North Node: {p('northNode')} | Chiron: {p('chiron')}
Black Moon Lilith: {p('blackMoonLilith')} | Part of Fortune: {p('partOfFortune')}

HUMAN DESIGN:
Type: {hd.get('type','')} | Strategy: {hd.get('strategy','')} | Authority: {hd.get('authority','')}
Profile: {hd.get('profile','')} | Definition: {hd.get('definition','')}
Incarnation Cross: {hd.get('incarnationCross','')}
Defined Centers: {', '.join(hd.get('definedCenters', []))}
Undefined Centers: {', '.join(hd.get('undefinedCenters', []))}
Active Gates: {', '.join(str(g) for g in hd.get('activeGates', []))}
Channels: {', '.join(hd.get('channels', []))}

NUMEROLOGY:
Name Number: {num.get('nameNumber', {}).get('raw', '')} reduced to {num.get('nameNumber', {}).get('reduced', '')}
Life Path: {num.get('lifePath', {}).get('raw', '')} reduced to {num.get('lifePath', {}).get('reduced', '')}
Birthday: {num.get('birthday', {}).get('reduced', '')}
Soul Urge: {num.get('soulUrge', {}).get('raw', '')} reduced to {num.get('soulUrge', {}).get('reduced', '')}
Personality: {num.get('personality', {}).get('raw', '')} reduced to {num.get('personality', {}).get('reduced', '')}
Personal Year: {num.get('personalYear', {}).get('reduced', '')}

HEBREW METATRON'S CUBE:
Dominant Element: {heb.get('dominantElement', '')}
Elemental Wounds: {', '.join(heb.get('elementalWounds', [])) or 'none'}
Convergence Power Points: {', '.join(str(c) for c in unique_convergence)}
Fibonacci Activations: {', '.join(str(f) for f in heb.get('fibonacciActivations', []))}

ACTIVATED POSITIONS (Layer 1 and Layer 2):
{chr(10).join(heb_lines)}

SELF-LOVE ASSESSMENT:
Score: {assess.get('selfLoveScore', '')} | Range: {assess.get('scoreRange', '')}
Attachment Style: {assess.get('attachmentStyle', '')}

GENERATION INSTRUCTIONS:

1. Output a [JOURNEY_MAP] block containing a JSON array of stops in this exact order.
   Position 21 Shin MUST be first. Position 0 The Fool MUST be last.
   Use EXACTLY this format with no variation:

[JOURNEY_MAP]
[{{"position": 21, "name": "Shin", "theme": "theme here"}}, {{"position": 9, "name": "Tet", "theme": "theme here"}}, {{"position": 0, "name": "The Fool", "theme": "theme here"}}]
[/JOURNEY_MAP]

2. Then for EACH position output a block using EXACTLY this format:
[POSITION_21]
reading text here
[/POSITION_21]

3. For EACH position in the journey map, output a [POSITION_N] block with the reading.
   Each reading should be 3-5 paragraphs, deeply personal, weaving together:
   - The Hebrew letter's meaning and frequency
   - The client's felt body response
   - Their astrology (relevant placements)
   - Their Human Design
   - Their numerology
   - Their career expression
   - Status-appropriate language (shadow=what is unprocessed, bridge=what is integrating, healed=what is complete)

4. MANDATORY: Include EVERY position in this list, no exceptions, no omissions: {_activated_str}. Plus position 0 as the final stop.
   No maximum limit on stops. Every activated position gets its own stop and its own reading.

5. Position 0 The Fool reading should be the closing blessing, the return to wholeness.

Begin generation now.
""".strip()

    return prompt


def _run_soul_blueprint_generation(payload: dict, job_id: str) -> None:
    try:
        heb = payload.get("hebrew", {})
        q = payload.get("assessment", {}).get("hebrewQuestionnaire", [])

        # Step 1: use stored statuses from DB, only reclassify if not present
        statuses = heb.get("positionStatuses") or _sb_classify_statuses(
            questionnaire=q,
            l1_positions=heb.get("layer1Positions", []),
            l2_positions=heb.get("layer2Positions", []),
            fib_activations=heb.get("fibonacciActivations", []),
        )
        payload["hebrew"]["positionStatuses"] = statuses

        # Build explicit list of all activated positions from Layer 1 and Layer 2 only
        all_activated_set = set()
        for p in heb.get("layer1Positions", []):
            pos = int(p.get("position", -1))
            if pos >= 0:
                all_activated_set.add(pos)
        for p in heb.get("layer2Positions", []):
            pos = int(p.get("position", -1))
            if pos >= 0:
                all_activated_set.add(pos)
        all_activated_set.discard(-1)
        payload["hebrew"]["allActivatedPositions"] = sorted(list(all_activated_set))

        # Step 2: build and send prompt to Claude
        prompt = _sb_build_prompt(payload)

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set on the server")

        claude_body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 16000,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=claude_body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=240) as resp:
            claude_data = json.loads(resp.read())

        result_text = claude_data["content"][0]["text"]

        # Step 3: parse [JOURNEY_MAP] and [POSITION_N] tags
        journey_match = re.search(r'\[JOURNEY_MAP\](.*?)\[/JOURNEY_MAP\]', result_text, re.DOTALL)
        if not journey_match:
            raise ValueError("No [JOURNEY_MAP] found in AI response")

        journey_json_str = journey_match.group(1).strip()
        journey_json_str = re.sub(r'^```\w*\n?', '', journey_json_str).rstrip('`').strip()
        journey_data = json.loads(journey_json_str)

        positions_text: dict = {}
        for pm in re.finditer(r'\[POSITION_(\d+)\](.*?)\[/POSITION_\1\]', result_text, re.DOTALL):
            positions_text[int(pm.group(1))] = pm.group(2).strip()

        # Step 4: build CHART from ALL activated positions (Layer 1 + Layer 2 only)
        l1 = heb.get("layer1Positions", [])
        l2 = heb.get("layer2Positions", [])

        pos_totals: dict = {}
        for p in l1:
            pos = int(p.get("position", -1))
            if pos >= 0:
                pos_totals[pos] = pos_totals.get(pos, 0) + 1
        for p in l2:
            pos = int(p.get("position", -1))
            if pos >= 0:
                pos_totals[pos] = pos_totals.get(pos, 0) + 1

        STATUS_WEIGHT = {"shadow": 0, "bridge": 1, "healed": 2, "not_activated": 3}

        def sort_key(pos):
            if pos == 21:
                return (0, 0, 0)
            if pos == 0:
                return (3, 0, 0)
            w = STATUS_WEIGHT.get(statuses.get(str(pos), "not_activated"), 3)
            return (1, w, -pos_totals.get(pos, 0))

        sorted_positions = sorted(all_activated_set, key=sort_key)

        NAME_MAP = {0:"The Fool",1:"Aleph",2:"Bet",3:"Gimel",4:"Dalet",5:"Heh",6:"Vav",7:"Zayin",8:"Chet",9:"Tet",10:"Yod",11:"Kaf",12:"Lamed",13:"Mem",14:"Nun",15:"Samech",16:"Ayin",17:"Peh",18:"Tzadi",19:"Qof",20:"Resh",21:"Shin",22:"Tav"}
        ELEM_MAP = {0:"Void",1:"Air",2:"Earth",3:"Fire",4:"Earth",5:"Air",6:"Earth",7:"Air",8:"Water",9:"Earth",10:"Fire",11:"Fire",12:"Air",13:"Water",14:"Water",15:"Fire",16:"Earth",17:"Air",18:"Water",19:"Earth",20:"Air",21:"Fire",22:"Earth"}

        chart = []
        for pos in sorted_positions:
            status = statuses.get(str(pos), "not_activated")
            felt = None
            if pos > 0:
                qi = next((r for r in q if int(r.get("position", 0)) == pos), None)
                if qi:
                    felt = (qi.get("feltResponse") or "").strip() or None
            chart.append({
                "position": pos,
                "status": status,
                "activation_count": pos_totals.get(pos, 0),
                "reading": positions_text.get(pos, ""),
                "felt_response": felt,
                "rebirth_client": None,
            })

        # NOT_THIS_LIFETIME positions
        not_this_lifetime = []
        for r in q:
            pos = int(r.get("position", 0))
            felt = (r.get("feltResponse") or "").strip()
            if felt and pos not in all_activated_set and pos != 0:
                status = statuses.get(str(pos), "not_activated")
                if status != "not_activated":
                    not_this_lifetime.append({
                        "position": pos,
                        "name": NAME_MAP.get(pos, ""),
                        "element": ELEM_MAP.get(pos, ""),
                        "status": status,
                        "felt_response": felt,
                    })

        # Step 5: populate HTML template
        template_path = Path(__file__).parent / "tcm-system" / "hebrew_metatron_cube_template.html"
        html = template_path.read_text(encoding="utf-8")

        client_d = payload.get("client", {})
        client_name = f"{client_d.get('firstName', '')} {client_d.get('lastName', '')}".strip()
        client_dob = client_d.get("dateOfBirth", "")

        pos0_text = positions_text.get(0, "")
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', pos0_text) if s.strip()]
        closing_line = sentences[-1] if sentences else "Your Soul Blueprint has always known the way."

        client_json = json.dumps({"name": client_name, "dob": client_dob, "closing": closing_line}, ensure_ascii=False)
        chart_json = json.dumps(chart, ensure_ascii=False)
        ntl_json = json.dumps(not_this_lifetime, ensure_ascii=False)
        all_statuses_json = json.dumps({str(i): statuses.get(str(i), "not_activated") for i in range(23)}, ensure_ascii=False)
        all_felt_dict = {}
        for r in q:
            pos = int(r.get("position", 0))
            felt = (r.get("feltResponse") or "").strip()
            if felt:
                all_felt_dict[str(pos)] = felt
        all_felt_json = json.dumps(all_felt_dict, ensure_ascii=False)

        # Use str.replace NOT re.sub
        html = html.replace(
            '// CLIENT_DATA_START\nconst CLIENT = {\n  name: "CLIENT_NAME",\n  dob: "CLIENT_DOB",\n  closing: "CLIENT_CLOSING"\n};',
            f'// CLIENT_DATA_START\nconst CLIENT = {client_json};',
        )
        html = html.replace(
            '// CHART_DATA_START\nconst CHART = [];',
            f'// CHART_DATA_START\nconst CHART = {chart_json};',
        )
        html = html.replace(
            '// NTL_DATA_START\nconst NOT_THIS_LIFETIME = [];',
            f'// NTL_DATA_START\nconst NOT_THIS_LIFETIME = {ntl_json};',
        )
        html = html.replace(
            '// ALL_STATUSES_START\nconst ALL_STATUSES = {};',
            f'// ALL_STATUSES_START\nconst ALL_STATUSES = {all_statuses_json};',
        )
        html = html.replace(
            '// ALL_FELT_START\nconst ALL_FELT = {};',
            f'// ALL_FELT_START\nconst ALL_FELT = {all_felt_json};',
        )

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result": html}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


def _parse_time(time_str: str):
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

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for k, v in CORS_HEADERS:
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path in ("/health", "/"):
            self._send_json(200, {"status": "ok"})
        elif path.startswith("/job-status/"):
            job_id = path[len("/job-status/"):]
            with _JOBS_LOCK:
                job = dict(_JOBS.get(job_id, {}))
            if not job:
                self._send_json(404, {"error": "job not found"})
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

        elif path == "/generate-soul-blueprint-tier1":
            client = payload.get("client", {})
            if not client.get("firstName") or not client.get("lastName"):
                self._send_json(400, {"error": "client.firstName and client.lastName are required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_soul_blueprint_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

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
                year, month, day, hour, minute,
                float(latitude), float(longitude), tz_value, 88,
            )
        elif location:
            chart = human_design_chart_from_intake(
                year, month, day, hour, minute, location,
                timezone_offset=timezone_offset,
                timezone_name=timezone_name,
                country_hint=country_hint,
                design_offset_days=88,
            )
        else:
            raise ValueError("Either 'location' or both 'latitude' and 'longitude' must be provided")

        return chart

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server(port: int, ephe_path: Optional[str]) -> None:
    print(f"run_server called with port={port}", flush=True)
    set_ephemeris_path(ephe_path)
    print(f"ephemeris path set, binding HTTPServer on port {port}", flush=True)
    try:
        server = HTTPServer(("", port), LocalAPIHandler)
    except Exception as e:
        print(f"FATAL: HTTPServer bind failed on port {port}: {e}", flush=True)
        raise
    print(f"Local API running on http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    parser.add_argument("--ephe-path", required=False, default=None)
    args = parser.parse_args()
    run_server(args.port, args.ephe_path)
