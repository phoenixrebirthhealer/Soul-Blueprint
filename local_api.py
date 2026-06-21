import argparse
import base64
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
 
from transformation_pdf import generate_transformation_pdf
 
_JOBS: dict = {}
_JOBS_LOCK = threading.Lock()
 
print("local_api.py: starting imports", flush=True)
try:
    print("local_api.py: attempting imports", flush=True)
    from astrology_humandesign import (
        human_design_chart,
        human_design_chart_from_intake,
        set_ephemeris_path,
        gate_from_longitude,
        CHANNEL_DEFINITIONS,
        CENTER_GATE_MAP,
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
You are writing a creative spiritual activation document. This is NOT a psychological assessment. This is NOT therapy. This is a soul mirror, a sacred creative work that reflects back to a person what their own soul already knows.
 
VOICE (NON-NEGOTIABLE):
- Write directly to the person as if you are their soul speaking back to them
- Be intimate, piercing, specific. Not warm and general. SPECIFIC.
- Do not explain the system. NEVER say "Layer 1" or "Layer 2". If you must reference the source of an activation, say "your name" or "your birth date" instead. Do not say "activations suggest." Speak the truth directly.
- Do not hedge. Do not soften with "may" or "might" or "suggests." Speak with certainty.
- Never use em dashes (anywhere, ever)
- Never use the word "medicine" - use "Rebirth" instead
- Never use "disorder/condition/diagnosis" - use "wiring pattern" or "soul design"
- This system is called Phoenix Rebirth Numerology / Hebrew Metatron's Cube
- Readings ACTIVATE Rebirths, they do not give advice
- Write as if you already know this person at a soul level. Because you do.
- The felt body response is GOLD. Build the entire reading around it. It is the most important data point.
- Status meanings, woven in naturally without labeling them: healed = this is already yours, fully lived; bridge = this is the active fire you are walking through right now; shadow = this is what is calling to be seen, what has been waiting in the dark
- Position 21 Shin is ALWAYS the first stop
- Position 0 The Fool is ALWAYS the final stop
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
   Then immediately after the reading paragraphs, still inside the [POSITION_N] block, add a [REBIRTH_N] block:
   [REBIRTH_21]
   One to three sentences. Direct. Personal. Written as if the soul itself is speaking. This is not advice. This is an activation. It names exactly what is being reclaimed, released, or ignited at this position. Use the client's name. Reference their felt response. Make it land in the body.
   [/REBIRTH_21]
 
4. MANDATORY: Include EVERY position in this list, no exceptions, no omissions: {_activated_str}. Plus position 0 as the final stop.
   No maximum limit on stops. Every activated position gets its own stop and its own reading.
 
5. Position 0 The Fool reading should be the closing blessing, the return to wholeness.
 
Begin generation now.
""".strip()
 
    return prompt
 
 
# ---------------------------------------------------------------------------
# Name Frequency
# ---------------------------------------------------------------------------
 
PHOENIX_LETTER_MAP = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,'J':10,
    'K':11,'L':12,'M':13,'N':14,'O':15,'P':16,'Q':17,'R':18,'S':19,'T':20,
    'U':21,'V':22,'W':23,'X':24,'Y':25,'Z':26
}
 
PHOENIX_CHAKRA_KEY = {
    0:'Soul in Purest Form',1:'Root',2:'Sacral',3:'Solar Plexus',4:'Heart',
    5:'Throat',6:'Third Eye',7:'Crown',8:'Soul Star',9:'Earth Star',
    11:'Double Root',22:'Double Sacral',33:'Double Solar Plexus'
}
 
MASTER_NUMBERS = {11, 22, 33}
 
def _nf_chakra_label(value: int) -> str:
    if value in MASTER_NUMBERS:
        return PHOENIX_CHAKRA_KEY[value]
    if value <= 9:
        return PHOENIX_CHAKRA_KEY.get(value, 'Soul in Purest Form')
    tens = value // 10
    ones = value % 10
    return f"{PHOENIX_CHAKRA_KEY.get(tens,'Soul in Purest Form')} leads {PHOENIX_CHAKRA_KEY.get(ones,'Soul in Purest Form')}"
 
def _nf_calculate(full_name: str) -> list:
    words = full_name.upper().strip().split()
    result = []
    for word in words:
        letters = []
        for ch in word:
            if ch.isalpha():
                value = PHOENIX_LETTER_MAP.get(ch, 0)
                letters.append({
                    "letter": ch,
                    "value": value,
                    "chakraLabel": _nf_chakra_label(value),
                })
        result.append({"word": word, "letters": letters})
    return result
 
def _run_name_frequency_generation(payload: dict, job_id: str) -> None:
    try:
        client_d = payload.get("client", {})
        full_name = payload.get("fullName", "")
        if not full_name:
            first = client_d.get("firstName", "")
            middle = client_d.get("middleName", "")
            maiden = client_d.get("maidenName", "")
            last = client_d.get("lastName", "")
            last_to_use = maiden if maiden and maiden != last else last
            full_name = " ".join(filter(None, [first, middle, last_to_use]))
 
        name_data = _nf_calculate(full_name)
 
        voice_rules = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Unfiltered, direct, warm, fierce.
Never use em dashes anywhere. Not once. Not ever.
Never use the word medicine. Always use Rebirth instead.
Never use disorder, condition, or diagnosis.
Master numbers are NEVER reduced. Ever.
Before you inform, you recognize. Before you analyze, you witness.
Every word must pass one test: Would this person feel SEEN? Not informed. SEEN.
The reading is a confirmation of what was always true. Not an analysis of what might be.
Write as if the name has always known who this person is.
Say it in the simplest words that still carry the full truth.
Short sentences land harder than long ones. Use them.
One idea per paragraph. Two at most.
Depth is not the same as complexity. Go deep. Stay simple."""
 
        name_labels = [f"{w['word']} ({', '.join(l['letter']+'='+str(l['value'])+' '+l['chakraLabel'] for l in w['letters'])})" for w in name_data]
 
        prompt = f"""{voice_rules}
 
You are generating a Name Frequency Reading for {full_name}.
 
The letter values and chakra labels have already been calculated by code.
Use these exact values. Do not recalculate. Do not reinterpret the numbers.
Your job is to write the human meaning around the data that has already been computed.
 
NAME FREQUENCY DATA (pre-calculated):
{chr(10).join(name_labels)}
 
WHAT TO WRITE FOR EACH LETTER:
- Name what this chakra frequency IS at its most essential
- Name what it means that this frequency appears at THIS position in THIS name
- Name what it means for how this soul gives, receives, and expresses love
- Write 2-3 substantial paragraphs per letter. Never a single sentence.
- Never be generic. Every sentence must be specific to this letter in this name.
 
WHAT TO WRITE FOR EACH NAME SUMMARY:
- Synthesize the arc of the whole name as one complete journey
- Name any repeated frequencies within this name and what the repetition means
- Name how this name prepares the soul for the next name (if there is one)
 
WHAT TO WRITE FOR THE FULL JOURNEY SECTION (minimum 6 paragraphs):
- Synthesize all names as one complete soul arc
- Name every repeated frequency across all names and what it insists on
- Name how the names close differently or the same and what that means
 
WHAT TO WRITE FOR THE LOVE IN YOUR FREQUENCY SECTION (minimum 3 paragraphs):
- Draw out only the frequencies that speak to how this soul loves and is loved
- Name the specific letters and positions that carry these frequencies
- Close with a sentence pointing toward the Self-Love Language Reading
 
OUTPUT FORMAT — CRITICAL:
Return structured data as JSON only. No HTML. No preamble. No markdown fences.
Return a JSON object with this exact structure:
{{
  "names": [
    {{
      "word": "FIRSTNAME",
      "eyebrow": "First Name",
      "tagline": "one evocative line",
      "letters": [
        {{"letter": "A", "value": 1, "chakraLabel": "Root", "chakraTag": "Root", "text": "full reading text here"}}
      ],
      "summary": "full name summary paragraph here"
    }}
  ],
  "fullJourney": "full journey text with paragraph breaks using \\n\\n",
  "loveInFrequency": "love in your frequency text with paragraph breaks using \\n\\n",
  "closingLine": "one closing line for this specific soul"
}}
 
The eyebrow for each name should be: First Name, Middle Name, Last Name (in order).
The chakraTag for each letter should be the short version for the left marker (e.g. "Root leads\\nSacral" with a newline for two-line tags).
Every text field must be specific to this person. Never generic.
"""
 
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
        with urllib.request.urlopen(req, timeout=600) as resp:
            claude_data = json.loads(resp.read())
 
        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        reading = json.loads(result_text)
 
        # Build HTML from template
        template_path = Path(__file__).parent / "tcm-system" / "name_frequency_template.html"
        html = template_path.read_text(encoding="utf-8")
 
        # Build nav buttons
        nav_html = ""
        for i, nm in enumerate(reading["names"]):
            active = " active" if i == 0 else ""
            nav_html += f'<button class="nav-btn{active}" onclick="showSection({i})">{nm["word"]}</button>\n'
        nav_html += f'<button class="nav-btn" onclick="showSection({len(reading["names"])})">The Full Journey</button>\n'
 
        # Build section HTML
        sections_html = ""
        name_labels_list = ["First Name", "Middle Name", "Last Name"]
        total_sections = len(reading["names"]) + 1
        for i, nm in enumerate(reading["names"]):
            active = " active" if i == 0 else ""
            prev_btn = f'<button class="nav-arrow hidden">&#8592; Previous</button>' if i == 0 else f'<button class="nav-arrow" onclick="showSection({i-1})">&#8592; {reading["names"][i-1]["word"]}</button>'
            if i < len(reading["names"]) - 1:
                next_btn = f'<button class="nav-arrow" onclick="showSection({i+1})">{reading["names"][i+1]["word"]} &#8594;</button>'
            else:
                next_btn = f'<button class="nav-arrow" onclick="showSection({i+1})">The Full Journey &#8594;</button>'
 
            dots = "".join([f'<div class="dot{" active" if j==i else ""}" onclick="showSection({j})"></div>' for j in range(total_sections)])
 
            letters_html = ""
            for lt in nm["letters"]:
                chakra_tag = lt.get("chakraTag", lt.get("chakraLabel", "")).replace("\\n", "<br>")
                letters_html += f"""
    <div class="letter-card">
      <div class="letter-marker">
        <div class="letter-glyph">{lt["letter"]}</div>
        <div class="letter-num">{lt["value"]}</div>
        <div class="letter-chakra-tag">{chakra_tag}</div>
      </div>
      <div class="letter-content">
        <div class="chakra-label">{lt["chakraLabel"]}</div>
        <div class="letter-text">{lt["text"]}</div>
      </div>
    </div>"""
 
            sections_html += f"""
  <div class="reading-section{active}" id="section-{i}">
    <div class="section-header">
      <div class="section-eyebrow">{nm["eyebrow"]}</div>
      <h2>{" ".join(nm["word"])}</h2>
      <p class="tagline">{nm["tagline"]}</p>
    </div>
    {letters_html}
    <div class="name-summary">
      <div class="summary-label">{nm["word"]} as a Whole</div>
      <div class="summary-text">{nm["summary"]}</div>
    </div>
    <div class="nav-bottom">
      {prev_btn}
      <div class="section-dots">{dots}</div>
      {next_btn}
    </div>
  </div>"""
 
        # Full journey section
        journey_idx = len(reading["names"])
        dots = "".join([f'<div class="dot{" active" if j==journey_idx else ""}" onclick="showSection({j})"></div>' for j in range(total_sections)])
        prev_name = reading["names"][-1]["word"]
        full_journey_paras = "".join([f"<p>{p}</p>" for p in reading["fullJourney"].split("\n\n") if p.strip()])
        love_paras = "".join([f"<p>{p}</p>" for p in reading["loveInFrequency"].split("\n\n") if p.strip()])
 
        sections_html += f"""
  <div class="reading-section" id="section-{journey_idx}">
    <div class="section-header">
      <div class="section-eyebrow">The Complete Soul Journey</div>
      <h2>{full_name}</h2>
      <p class="tagline">The whole story in one arc.</p>
    </div>
    <div class="integration">
      <div class="integration-title">The Full Soul Journey</div>
      <div class="integration-text">{full_journey_paras}</div>
    </div>
    <div class="bridge">
      <div class="bridge-title">The Love in Your Frequency</div>
      <div class="bridge-text">{love_paras}</div>
    </div>
    <div class="closing">
      <div class="closing-line">{reading["closingLine"]}</div>
      <div class="closing-attribution">Phoenix Rebirth | Name Frequency Reading | Christina Stevens</div>
    </div>
    <div class="nav-bottom">
      <button class="nav-arrow" onclick="showSection({journey_idx-1})">&#8592; {prev_name}</button>
      <div class="section-dots">{dots}</div>
      <button class="nav-arrow hidden">Next &#8594;</button>
    </div>
  </div>"""
 
        # Inject into template
        html = html.replace("<!--NAMFREQ_CLIENT_NAME-->", full_name)
        html = html.replace("<!--NAMFREQ_NAV_START-->\n    <button class=\"nav-btn active\" onclick=\"showSection(0)\">AMBER</button>\n    <button class=\"nav-btn\" onclick=\"showSection(1)\">NICOLE</button>\n    <button class=\"nav-btn\" onclick=\"showSection(2)\">LINGLE</button>\n    <button class=\"nav-btn\" onclick=\"showSection(3)\">The Full Journey</button>\n    <!--NAMFREQ_NAV_END-->", f"<!--NAMFREQ_NAV_START-->\n    {nav_html}    <!--NAMFREQ_NAV_END-->")
        html = html.replace(f'<!--NAMFREQ_CONTENT_START-->', '<!--NAMFREQ_CONTENT_START-->')
 
        # Replace everything between content markers
        content_pattern = re.compile(r'<!--NAMFREQ_CONTENT_START-->.*?<!--NAMFREQ_CONTENT_END-->', re.DOTALL)
        html = content_pattern.sub(f'<!--NAMFREQ_CONTENT_START-->{sections_html}\n  <!--NAMFREQ_CONTENT_END-->', html)
 
        html = html.replace("<!--NAMFREQ_FOOTER-->", f"Phoenix Rebirth &nbsp;&bull;&nbsp; Name Frequency Reading &nbsp;&bull;&nbsp; {full_name} &nbsp;&bull;&nbsp; Proprietary &nbsp;&bull;&nbsp; 2026")
 
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result": html}
 
    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}
 
 
 
def _run_soul_blueprint_generation(payload: dict, job_id: str) -> None:
    try:
        heb = payload.get("hebrew", {})
        q = payload.get("assessment", {}).get("hebrewQuestionnaire", [])
 
        raw_statuses = heb.get("positionStatuses")
        if isinstance(raw_statuses, dict) and raw_statuses:
            statuses = raw_statuses
        else:
            statuses = _sb_classify_statuses(
                questionnaire=q,
                l1_positions=heb.get("layer1Positions", []),
                l2_positions=heb.get("layer2Positions", []),
                fib_activations=heb.get("fibonacciActivations", []),
            )
        payload["hebrew"]["positionStatuses"] = statuses
 
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
        with urllib.request.urlopen(req, timeout=600) as resp:
            claude_data = json.loads(resp.read())
 
        result_text = claude_data["content"][0]["text"]
 
        journey_match = re.search(r'\[JOURNEY_MAP\](.*?)\[/JOURNEY_MAP\]', result_text, re.DOTALL)
        if not journey_match:
            raise ValueError("No [JOURNEY_MAP] found in AI response")
 
        journey_json_str = journey_match.group(1).strip()
        journey_json_str = re.sub(r'^```\w*\n?', '', journey_json_str).rstrip('`').strip()
        journey_data = json.loads(journey_json_str)
 
        positions_text: dict = {}
        rebirths_text: dict = {}
        for pm in re.finditer(r'\[POSITION_(\d+)\](.*?)\[/POSITION_\1\]', result_text, re.DOTALL):
            pos_num = int(pm.group(1))
            full_block = pm.group(2).strip()
            rebirth_match = re.search(r'\[REBIRTH_' + str(pos_num) + r'\](.*?)\[/REBIRTH_' + str(pos_num) + r'\]', full_block, re.DOTALL)
            if rebirth_match:
                rebirths_text[pos_num] = rebirth_match.group(1).strip()
                reading_only = re.sub(r'\[REBIRTH_' + str(pos_num) + r'\].*?\[/REBIRTH_' + str(pos_num) + r'\]', '', full_block, flags=re.DOTALL).strip()
                positions_text[pos_num] = reading_only
            else:
                positions_text[pos_num] = full_block
 
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
                "rebirth_client": rebirths_text.get(pos, None),
            })
 
        not_this_lifetime = []
        for r in q:
            pos = int(r.get("position", 0))
            felt = (r.get("feltResponse") or "").strip()
            if felt and pos not in all_activated_set and pos != 0:
                not_this_lifetime.append({
                    "position": pos,
                    "name": NAME_MAP.get(pos, ""),
                    "element": ELEM_MAP.get(pos, ""),
                    "status": "not_activated",
                    "felt_response": felt,
                })
 
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
 
 
import swisseph as _swe

_SIGNS_LIST = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

_SIGN_RULERS = {
    'Aries':       ['mars'],
    'Taurus':      ['venus'],
    'Gemini':      ['mercury'],
    'Cancer':      ['moon'],
    'Leo':         ['sun'],
    'Virgo':       ['mercury'],
    'Libra':       ['venus'],
    'Scorpio':     ['mars'],
    'Sagittarius': ['jupiter'],
    'Capricorn':   ['saturn'],
    'Aquarius':    ['saturn'],
    'Pisces':      ['jupiter'],
}

_PLANET_IDS_TRANSIT = {
    'sun':     _swe.SUN,
    'moon':    _swe.MOON,
    'mercury': _swe.MERCURY,
    'venus':   _swe.VENUS,
    'mars':    _swe.MARS,
    'jupiter': _swe.JUPITER,
    'saturn':  _swe.SATURN,
    'uranus':  _swe.URANUS,
    'neptune': _swe.NEPTUNE,
    'pluto':   _swe.PLUTO,
    'chiron':  _swe.CHIRON,
    'northnode': _swe.TRUE_NODE,
    'blackmoonlilith': _swe.MEAN_APOG,
}


def _transit_date_to_jd(d):
    return _swe.julday(d.year, d.month, d.day, 12.0)


def _transit_get_longitude(planet_id, jd):
    result, _ = _swe.calc_ut(jd, planet_id, _swe.FLG_SWIEPH)
    return result[0]


def calculate_todays_planet_positions() -> dict:
    """
    Calculate the current sky position (sign, degree, retrograde) for all
    major planets, as of right now. This is the single source of truth
    for 'where are the planets today' used by every reading that needs it.
    The Moon additionally gets a start-of-day and end-of-day calculation,
    since it moves roughly half a degree per hour and a single midnight
    snapshot would be inaccurate by evening.
    """
    from datetime import date as _date, datetime as _dt

    today = _date.today()
    jd_now = _transit_date_to_jd(today)

    positions = {}
    for planet_key, planet_id in _PLANET_IDS_TRANSIT.items():
        try:
            lon = _transit_get_longitude(planet_id, jd_now)
            sign_idx = int(lon // 30)
            # Retrograde check: compare position now vs. position 1 day ago
            jd_yesterday = jd_now - 1
            lon_yesterday = _transit_get_longitude(planet_id, jd_yesterday)
            diff = lon - lon_yesterday
            if diff > 180: diff -= 360
            if diff < -180: diff += 360
            is_retrograde = diff < 0

            positions[planet_key] = {
                'sign': _SIGNS_LIST[sign_idx],
                'degree': round(lon % 30, 2),
                'longitude': round(lon, 4),
                'retrograde': is_retrograde,
            }
        except Exception:
            continue

    # South Node is always exactly opposite North Node — derived, not looked up
    if 'northnode' in positions:
        nn_lon = positions['northnode']['longitude']
        sn_lon = (nn_lon + 180) % 360
        sn_sign_idx = int(sn_lon // 30)
        positions['southnode'] = {
            'sign': _SIGNS_LIST[sn_sign_idx],
            'degree': round(sn_lon % 30, 2),
            'longitude': round(sn_lon, 4),
            'retrograde': positions['northnode']['retrograde'],
        }

    # Moon-specific: exact start-of-day (00:00) and end-of-day (23:59) positions,
    # since the Moon moves too fast for a single snapshot to represent the whole day.
    try:
        jd_start = _swe.julday(today.year, today.month, today.day, 0.0)
        jd_end   = _swe.julday(today.year, today.month, today.day, 23.983333)

        moon_lon_start = _transit_get_longitude(_swe.MOON, jd_start)
        moon_lon_end   = _transit_get_longitude(_swe.MOON, jd_end)

        moon_sign_start_idx = int(moon_lon_start // 30)
        moon_sign_end_idx   = int(moon_lon_end // 30)

        positions['moon_day_arc'] = {
            'start': {
                'sign': _SIGNS_LIST[moon_sign_start_idx],
                'degree': round(moon_lon_start % 30, 2),
                'longitude': round(moon_lon_start, 4),
            },
            'end': {
                'sign': _SIGNS_LIST[moon_sign_end_idx],
                'degree': round(moon_lon_end % 30, 2),
                'longitude': round(moon_lon_end, 4),
            },
            'changes_sign': moon_sign_start_idx != moon_sign_end_idx,
        }
    except Exception:
        pass

    return {
        'date': today.isoformat(),
        'positions': positions,
    }
def get_current_profection_year(birth_date_str: str, rising_sign: str, as_of_date=None, cached_positions=None) -> dict:
    """
    Calculate the CURRENT real-time Profection year: activated house, activated sign,
    ruling planet(s) (Time Lord), and current transiting positions of the Time Lord(s).
    birth_date_str: 'YYYY-MM-DD'
    rising_sign: e.g. 'Aquarius'
    cached_positions: optional dict of today's already-calculated planet positions
    (the same shape returned by calculate_todays_planet_positions()['positions']).
    When provided, this is used instead of recalculating the sky, so every reading
    that needs 'today's sky' agrees with the single nightly cron calculation.
    Returns dict with age, activated_house, activated_sign, activated_rulers,
    and current_transit_positions (longitude + sign + house-relative-to-natal for each Time Lord).
    """
    from datetime import datetime as _dt, date as _date

    if as_of_date is None:
        as_of_date = _date.today()

    birth_date = _dt.strptime(birth_date_str, '%Y-%m-%d').date()

    age = as_of_date.year - birth_date.year
    if (as_of_date.month, as_of_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    house_index = age % 12
    activated_house = house_index + 1

    rising_index = _SIGNS_LIST.index(rising_sign) if rising_sign in _SIGNS_LIST else 0
    activated_sign_index = (rising_index + house_index) % 12
    activated_sign = _SIGNS_LIST[activated_sign_index]
    activated_rulers = _SIGN_RULERS.get(activated_sign, [])

    current_transit_positions = {}

    if cached_positions:
        # Use the single source of truth from the nightly cache instead of recalculating.
        for ruler in activated_rulers:
            pos = cached_positions.get(ruler)
            if pos:
                current_transit_positions[ruler] = {
                    'longitude': pos.get('longitude'),
                    'sign': pos.get('sign'),
                    'degree': pos.get('degree'),
                }
    else:
        # Fallback: no cache provided, calculate directly (legacy behavior, kept for safety).
        jd_now = _transit_date_to_jd(as_of_date)
        for ruler in activated_rulers:
            planet_id = _PLANET_IDS_TRANSIT.get(ruler)
            if planet_id is None:
                continue
            try:
                lon = _transit_get_longitude(planet_id, jd_now)
                sign_idx = int(lon // 30)
                current_transit_positions[ruler] = {
                    'longitude': lon,
                    'sign': _SIGNS_LIST[sign_idx],
                    'degree': round(lon % 30, 2),
                }
            except Exception:
                continue

    return {
        'age': age,
        'activated_house': activated_house,
        'activated_sign': activated_sign,
        'activated_rulers': activated_rulers,
        'current_transit_positions': current_transit_positions,
    }

def calculate_daily_hd_gate_activations(today_positions: dict, natal_planet_positions: list) -> dict:
    """
    For each transiting planet today, determine:
    1. Which Human Design Gate it is currently activating (mechanical, via gate_from_longitude)
    2. Whether that Gate matches one of the person's own natal Gates (reinforcement)
    3. Whether that Gate completes a Channel with one of the person's natal Gates (temporary channel)

    natal_planet_positions: the raw 'birth'.'planet_positions' list already stored
    in client_calculations.astrology_data, each entry having a 'gate' key.

    Returns a dict keyed by planet name with activation details, e.g.:
    {
      'sun': {
        'transit_gate': 51,
        'is_reinforcement': True,
        'reinforced_natal_planet': 'Sun',
        'channel_completions': [{'channel': 'Initiation', 'natal_gate': 25, 'natal_planet': 'Venus'}]
      },
      ...
    }
    All mechanical, code-only, never left to AI interpretation.
    """
    # Build a lookup of natal gate number -> list of planets that carry that gate natally
    natal_gate_to_planets = {}
    natal_gate_set = set()
    for p in natal_planet_positions:
        gate = p.get("gate")
        planet_name = p.get("planet")
        if gate is None or planet_name is None:
            continue
        natal_gate_set.add(gate)
        natal_gate_to_planets.setdefault(gate, []).append(planet_name)

    activations = {}
    for planet_key, pos in today_positions.items():
        if planet_key == "moon_day_arc":
            continue
        lon = pos.get("longitude")
        if lon is None:
            continue

        transit_gate = gate_from_longitude(lon)
        is_reinforcement = transit_gate in natal_gate_set
        reinforced_planets = natal_gate_to_planets.get(transit_gate, []) if is_reinforcement else []

        channel_completions = []
        for channel in CHANNEL_DEFINITIONS:
            g1, g2 = channel["gates"]
            if transit_gate == g1 and g2 in natal_gate_set:
                for natal_planet in natal_gate_to_planets.get(g2, []):
                    channel_completions.append({
                        "channel": channel["name"],
                        "natal_gate": g2,
                        "natal_planet": natal_planet,
                        "centers": channel["centers"],
                    })
            elif transit_gate == g2 and g1 in natal_gate_set:
                for natal_planet in natal_gate_to_planets.get(g1, []):
                    channel_completions.append({
                        "channel": channel["name"],
                        "natal_gate": g1,
                        "natal_planet": natal_planet,
                        "centers": channel["centers"],
                    })

        activations[planet_key] = {
            "transit_gate": transit_gate,
            "is_reinforcement": is_reinforcement,
            "reinforced_natal_planets": reinforced_planets,
            "channel_completions": channel_completions,
        }

    return activations


_ASPECT_ANGLES = {
    'conjunction': 0,
    'sextile':     60,
    'square':      90,
    'trine':       120,
    'opposition':  180,
}
_ASPECT_ORB = 8.0


def _angular_difference(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two zodiac longitudes, 0-180."""
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def calculate_transit_to_natal_aspects(today_positions: dict, natal_planet_positions: list) -> list:
    """
    Compare today's transiting planets against the natal chart and return
    every active aspect within an 8-degree orb. This is the single shared
    engine used by Daily (deep), Weekly, and Monthly tiers -- built once,
    applied everywhere, so there is never a disagreement between tiers
    about what counts as an active transit-to-natal aspect.

    Returns a list of dicts:
    [{'transit_planet': 'mars', 'natal_planet': 'Venus', 'aspect': 'square',
      'orb': 2.3, 'transit_longitude': 53.3, 'natal_longitude': 51.0}, ...]
    """
    aspects_found = []

    for transit_key, transit_pos in today_positions.items():
        if transit_key == "moon_day_arc":
            continue
        transit_lon = transit_pos.get("longitude")
        if transit_lon is None:
            continue

        for natal_p in natal_planet_positions:
            natal_lon = natal_p.get("longitude")
            natal_name = natal_p.get("planet")
            if natal_lon is None or natal_name is None:
                continue

            diff = _angular_difference(transit_lon, natal_lon)

            for aspect_name, aspect_angle in _ASPECT_ANGLES.items():
                orb = abs(diff - aspect_angle)
                if orb <= _ASPECT_ORB:
                    aspects_found.append({
                        "transit_planet": transit_key,
                        "natal_planet": natal_name,
                        "aspect": aspect_name,
                        "orb": round(orb, 2),
                        "transit_longitude": round(transit_lon, 2),
                        "natal_longitude": round(natal_lon, 2),
                    })
                    break  # one planet pair can only form one aspect at a time

    # Sort tightest orb first -- the most exact, most significant aspects lead
    aspects_found.sort(key=lambda a: a["orb"])
    return aspects_found


def calculate_planet_positions_for_date(target_date) -> dict:
    """
    Calculate exact planet positions for ANY given date (past or future).
    Same engine as calculate_todays_planet_positions but parameterized by date,
    used for building multi-day windows for Weekly/Monthly aspect arcs.
    """
    jd = _transit_date_to_jd(target_date)
    positions = {}
    for planet_key, planet_id in _PLANET_IDS_TRANSIT.items():
        try:
            lon = _transit_get_longitude(planet_id, jd)
            positions[planet_key] = {'longitude': round(lon, 4)}
        except Exception:
            continue

    if 'northnode' in positions:
        nn_lon = positions['northnode']['longitude']
        sn_lon = (nn_lon + 180) % 360
        positions['southnode'] = {'longitude': round(sn_lon, 4)}

    return positions


def calculate_aspect_arcs_for_window(start_date, num_days: int, natal_planet_positions: list) -> list:
    """
    Calculates transit-to-natal aspects for EVERY day across a window
    (e.g. 7 days for Weekly, 30 for Monthly), then groups by planet-pair
    to find each aspect's real arc: the day it enters orb, the day it is
    most exact (tightest orb, the 'peak'), and the day it leaves orb.

    This is the single shared engine for Weekly and Monthly tiers, built
    once on top of the already-verified daily aspect engine, so both tiers
    always agree with each other and with the Daily tier about what an
    aspect IS, just viewed across a longer window.

    Returns a list of dicts, one per unique planet-pair aspect found
    anywhere in the window:
    [{'transit_planet': 'mars', 'natal_planet': 'Venus', 'aspect': 'square',
      'enters_orb_date': '2026-06-21', 'peak_date': '2026-06-24', 'peak_orb': 0.1,
      'exits_orb_date': '2026-06-27', 'still_active_at_window_end': False}, ...]
    """
    from datetime import timedelta

    # Track every (transit_planet, natal_planet, aspect_type) combo seen across the window
    arc_tracker = {}

    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        day_positions = calculate_planet_positions_for_date(current_date)
        day_aspects = calculate_transit_to_natal_aspects(day_positions, natal_planet_positions)

        seen_today = set()
        for asp in day_aspects:
            key = (asp["transit_planet"], asp["natal_planet"], asp["aspect"])
            seen_today.add(key)

            if key not in arc_tracker:
                arc_tracker[key] = {
                    "transit_planet": asp["transit_planet"],
                    "natal_planet": asp["natal_planet"],
                    "aspect": asp["aspect"],
                    "enters_orb_date": current_date.isoformat(),
                    "peak_date": current_date.isoformat(),
                    "peak_orb": asp["orb"],
                    "exits_orb_date": current_date.isoformat(),
                    "still_active_at_window_end": True,
                }
            else:
                entry = arc_tracker[key]
                entry["exits_orb_date"] = current_date.isoformat()
                if asp["orb"] < entry["peak_orb"]:
                    entry["peak_orb"] = asp["orb"]
                    entry["peak_date"] = current_date.isoformat()

        # Mark any tracked aspect NOT seen today as having exited orb (unless it's still day 0)
        for key, entry in arc_tracker.items():
            if key not in seen_today and entry["exits_orb_date"] != current_date.isoformat():
                entry["still_active_at_window_end"] = (entry["exits_orb_date"] == (start_date + timedelta(days=num_days - 1)).isoformat())

    arcs = list(arc_tracker.values())
    # Sort tightest peak orb first -- most significant aspects in the window lead
    arcs.sort(key=lambda a: a["peak_orb"])
    return arcs


# Planets ranked by how slow they move (slower = more weekly/monthly significance)
_PLANET_SPEED_WEIGHT = {
    'pluto': 10, 'neptune': 9, 'uranus': 8, 'saturn': 7, 'jupiter': 6,
    'chiron': 6, 'northnode': 5, 'southnode': 5, 'blackmoonlilith': 4,
    'mars': 3, 'sun': 2, 'venus': 2, 'mercury': 1, 'moon': 0,
}


def score_aspect_arcs_for_synthesis(arcs: list, num_days_in_window: int) -> list:
    """
    Scores and sorts aspect arcs by combined weight of (a) how many days they
    stay active across the window and (b) how slow-moving the transiting
    planet is. This surfaces the aspects that genuinely carry a week's or
    month's theme, rather than just the tightest single-day orb, which would
    favor fast Moon aspects over the slower, more thematically significant
    outer-planet aspects that actually define the period.

    Mutates nothing; returns a new sorted list with a 'synthesis_score' added.
    """
    from datetime import date as _date

    scored = []
    for arc in arcs:
        enter = _date.fromisoformat(arc["enters_orb_date"])
        exit_ = _date.fromisoformat(arc["exits_orb_date"])
        duration_days = (exit_ - enter).days + 1

        speed_weight = _PLANET_SPEED_WEIGHT.get(arc["transit_planet"], 1)
        # Tighter peak orb still matters, but less than duration/speed for this scoring
        orb_factor = max(0, 8 - arc["peak_orb"]) / 8  # 0 to 1, tighter orb = closer to 1

        synthesis_score = (duration_days * 2) + (speed_weight * 3) + (orb_factor * 4)

        new_arc = dict(arc)
        new_arc["duration_days"] = duration_days
        new_arc["synthesis_score"] = round(synthesis_score, 2)
        scored.append(new_arc)

    scored.sort(key=lambda a: -a["synthesis_score"])
    return scored


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
 

import math as _math
from datetime import date as _dt_date
 
_SLL_VOICE_RULES = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Unfiltered, direct, warm, fierce, funny. Profanity when it serves truth. Never use em dashes anywhere. Never say medicine, always say Rebirth. Never say disorder, condition, or diagnosis. Always use: wiring pattern, neurological architecture, soul chosen processing difference, nervous system design. Master numbers never reduced. The system activates Rebirths, it does not give advice.
DEPTH: This is a paid reading. Every section must be a minimum of 3 to 4 substantial paragraphs. Never 5 to 6 sentences. Write as if this person paid for the truth.""".strip()
 
 
def _sll_build_prompt_language(first_name, venus_sign, venus_house, moon_sign, moon_house, rising_sign, sl_score, sl_result, attachment_style):
    return f"""{_SLL_VOICE_RULES}

Write "The Language You Speak" section for {first_name}'s Self-Love Language Reading.

CLIENT DATA:
Venus: {venus_sign} House {venus_house}
Moon: {moon_sign} House {moon_house}
Rising: {rising_sign}
Self-love score: {sl_score}/85
Score range: {sl_result}
Attachment style: {attachment_style}

CRITICAL REQUIREMENT: You must name the actual placements explicitly in the text. State "Your Venus in {venus_sign} in the {venus_house}th house" in paragraph 1. State "Your Moon in {moon_sign} in the {moon_house}th house" in paragraph 2. State "Your {rising_sign} Rising" in paragraph 3. Never be vague about which placement you are reading. If you do not name the placement explicitly, the reading is wrong.

Write 3 to 4 substantial paragraphs. Paragraph 1: the intrinsic love language encoded in this person's Venus sign and house, the specific way they show care without thinking, the specific gestures and acts that come naturally and feel like love to them. Be specific to this Venus placement. Paragraph 2: how their Moon sign and house shapes how they receive love, what they need to feel safe enough to let love land, and what unconsciously signals to them that love is real versus performed. Paragraph 3: how their Rising sign shapes the first impression people get of their love nature, and how that impression sometimes misrepresents the depth underneath. Paragraph 4: how their self-love score and attachment style interact with everything named above, the patterns that show up in how they give and receive, and what becomes possible when this love language is finally understood and honored. Be warm, direct, and specific. No clinical language.

Return ONLY the reading text. No preamble. No labels. No JSON. Just the paragraphs separated by double newlines."""
 
 
def _sll_build_prompt_stolen(first_name, chiron_sign, chiron_house, saturn_sign, saturn_house, saturn_rx, snode_sign, snode_house, moon_sign, moon_house, rising_sign, sl_score, attachment_style, hebrew_felt):
    saturn_rx_str = " Rx" if saturn_rx else ""
    return f"""{_SLL_VOICE_RULES}

Write "Where Self-Love Got Stolen" for {first_name}'s Self-Love Language Reading.

CLIENT DATA:
Chiron: {chiron_sign} House {chiron_house}
Saturn: {saturn_sign} House {saturn_house}{saturn_rx_str}
South Node: {snode_sign} House {snode_house}
Moon: {moon_sign} House {moon_house}
Rising: {rising_sign}
Attachment style: {attachment_style}
Self-love score: {sl_score}/85

HEBREW QUESTIONNAIRE FELT RESPONSES (body-level truth):
{hebrew_felt}

CRITICAL REQUIREMENT: You must name every placement explicitly in the text. State "Chiron in {chiron_sign} in the {chiron_house}th house" in paragraph 1. State "Saturn in {saturn_sign} in the {saturn_house}th house{saturn_rx_str}" and "South Node in {snode_sign} in the {snode_house}th house" in paragraph 2. State "Moon in {moon_sign} in the {moon_house}th house" in paragraph 3. Never be vague about which placement you are reading. If you do not name the placement explicitly, the reading is wrong.

Write 3 to 4 substantial paragraphs. Paragraph 1: when and how self-love was first interrupted, based on the Chiron wound and the 4th house sign from ASC {rising_sign}, naming the specific environment and the specific message this child absorbed about their worth. Not blaming parents, naming the astrological imprint. Paragraph 2: the specific lie that was installed about their worthiness, based on Saturn and South Node. What did they learn they had to do, be, or prove in order to deserve love. Name the self-abandonment pattern this chart shows. Paragraph 3: what the Hebrew questionnaire felt responses reveal about where this wound lives in the body right now. If hebrew data is not completed, name what the Moon and Chiron placements suggest the body has been holding. Paragraph 4: one sentence of reclamation specific to this person's chart, followed by naming exactly what the reclamation path looks like. Be compassionate. Be direct. Do not soften the wound and do not leave them in it.

Return ONLY the reading text. No preamble. No labels. No JSON. Just the paragraphs separated by double newlines."""
 
 
def _sll_build_prompt_home(first_name, nnode_sign, nnode_house, mc_sign, venus_sign, venus_house, rising_sign, moon_sign, moon_house, hd_type, hd_authority, hd_profile, defined_centers, undefined_centers, channels, life_path, career_field, career_expression):
    return f"""{_SLL_VOICE_RULES}

Write "Coming Home" for {first_name}'s Self-Love Language Reading.

CLIENT DATA:
North Node: {nnode_sign} House {nnode_house}
Midheaven: {mc_sign}
Venus: {venus_sign} House {venus_house}
Rising: {rising_sign}
Moon: {moon_sign} House {moon_house}
Human Design type: {hd_type} | Authority: {hd_authority} | Profile: {hd_profile}
Defined Centers: {defined_centers}
Undefined Centers: {undefined_centers}
Channels: {channels}
Life Path: {life_path}
Career Field: {career_field}
Career Expression: {career_expression}

CRITICAL REQUIREMENT: You must name every placement explicitly in the text. State "Moon in {moon_sign} in the {moon_house}th house" in paragraph 1. State "Venus in {venus_sign} in the {venus_house}th house" in paragraph 2. State "North Node in {nnode_sign} in the {nnode_house}th house" and "Midheaven in {mc_sign}" in paragraph 3. State the Human Design type {hd_type} with {hd_authority} authority explicitly. Never be vague about which placement you are reading. If you do not name the placement explicitly, the reading is wrong.

Write 3 to 4 substantial paragraphs. Paragraph 1: what coming home to self-love looks like in the body for this specific person, grounded in their Moon sign and house, their Human Design defined centers, and any defined channels that speak directly to self-trust and inner authority. Name the specific practices that support this nervous system design. Paragraph 2: what coming home looks like in their values and creative expression, grounded in Venus sign and house and Human Design undefined centers. Name where their undefined centers have been absorbing other people's self-love patterns. Paragraph 3: what coming home looks like in their evolutionary direction and work in the world, grounded in North Node, Midheaven, and career data. Name specifically what self-love makes possible in their work that the wound was blocking. Paragraph 4: one powerful, specific, complete statement of what opens when they are finally home in themselves. Not a list. A direction. A felt sense of arrival.

Return ONLY the reading text. No preamble. No labels. No JSON. Just the paragraphs separated by double newlines."""
 
 
_DEGREE_TO_CHAKRA = {
    0: 'Crown', 1: 'Solar Plexus', 2: 'Heart', 3: 'Throat', 4: 'Third Eye', 5: 'Third Eye',
    6: 'Throat', 7: 'Heart', 8: 'Solar Plexus', 9: 'Sacral', 10: 'Root', 11: 'Root',
    12: 'Sacral', 13: 'Solar Plexus', 14: 'Heart', 15: 'Throat', 16: 'Third Eye', 17: 'Third Eye',
    18: 'Throat', 19: 'Heart', 20: 'Solar Plexus', 21: 'Sacral', 22: 'Root', 23: 'Root',
    24: 'Sacral', 25: 'Solar Plexus', 26: 'Heart', 27: 'Throat', 28: 'Third Eye', 29: 'Crown',
}

_CARDINAL_SIGNS = {'Aries', 'Cancer', 'Libra', 'Capricorn'}
_FIXED_SIGNS    = {'Taurus', 'Leo', 'Scorpio', 'Aquarius'}
_MUTABLE_SIGNS  = {'Gemini', 'Virgo', 'Sagittarius', 'Pisces'}


def _get_degree_chakra_and_criticality(degree_float, sign):
    deg_int = int(degree_float)
    chakra = _DEGREE_TO_CHAKRA.get(deg_int, 'Crown')

    criticality = None
    if deg_int == 0:
        criticality = 'Critical degree (all signs)'
    elif deg_int == 15:
        criticality = 'Critical degree (all signs)'
    elif deg_int == 25:
        criticality = 'Karmic degree (all signs)'
    elif deg_int == 29:
        criticality = 'Anaretic degree, karmic completion (all signs)'
    elif deg_int in (13, 26) and sign in _CARDINAL_SIGNS:
        criticality = 'Critical degree (cardinal sign)'
    elif deg_int in (8, 9, 21, 22) and sign in _FIXED_SIGNS:
        criticality = 'Critical degree (fixed sign)'
    elif deg_int in (4, 17) and sign in _MUTABLE_SIGNS:
        criticality = 'Critical degree (mutable sign)'
    elif deg_int == 0 and sign in _CARDINAL_SIGNS:
        criticality = 'Cardinal degree (0 of cardinal sign)'
    elif 8 <= deg_int <= 11 and sign in _FIXED_SIGNS:
        criticality = 'Fixed degree range'
    elif 21 <= deg_int <= 24 and sign in _MUTABLE_SIGNS:
        criticality = 'Mutable degree range'

    return chakra, criticality


# TCM (Traditional Chinese Medicine) correspondences per chakra, verified against
# Christina's proprietary system. Derived directly from the chakra already
# calculated by degree, no separate calculation needed.
_TCM_CHAKRA_MAP = {
    'Root':         {'element': 'Water',      'yin_meridian': 'Kidney',          'yang_meridian': 'Bladder'},
    'Sacral':       {'element': 'Earth/Wood',  'yin_meridian': 'Liver/Spleen',    'yang_meridian': 'Spleen/Liver'},
    'Solar Plexus': {'element': 'Earth/Wood',  'yin_meridian': 'Spleen',          'yang_meridian': 'Stomach/Gallbladder'},
    'Heart':        {'element': 'Fire',        'yin_meridian': 'Heart',           'yang_meridian': 'Pericardium'},
    'Throat':       {'element': 'Metal',       'yin_meridian': 'Lung',            'yang_meridian': 'Large Intestine'},
    'Third Eye':    {'element': 'Fire/Wood',   'yin_meridian': 'Small Intestine', 'yang_meridian': 'Triple Burner'},
    'Crown':        {'element': 'All/Spirit',  'yin_meridian': 'Governing Vessel','yang_meridian': 'Governing Vessel'},
}


def get_tcm_for_chakra(chakra: str) -> dict:
    """Returns the TCM element + meridian pair for a given chakra, mechanical lookup."""
    return _TCM_CHAKRA_MAP.get(chakra, {})


_CHAKRA_MEANINGS = {
    'Root':         'foundation, grounding, physical presence, core identity',
    'Sacral':       'creative energy, generative force, life force expression',
    'Solar Plexus': 'personal power, will, confidence, the fire of self',
    'Heart':        'love, connection, giving and receiving',
    'Throat':       'authentic voice, expression, truth in sound',
    'Third Eye':    'intuition, inner vision, expanded perception',
    'Crown':        'divine connection, higher consciousness, the infinite',
}


_DAILY_TRANSIT_VOICE_RULES = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Direct, warm, fierce. Never use em dashes anywhere. Never say medicine, say Rebirth. Never say disorder, condition, or diagnosis. Master numbers never reduced.
LENGTH: Each planet gets exactly 2 to 3 sentences. This is a daily snapshot, not a deep reading. Be specific and punchy, not vague.""".strip()


def _build_daily_transit_prompt(client_name, today_positions, natal_signs, natal_houses, natal_aspects, chakra_data_out=None, hd_gate_activations=None):
    planet_lines = []
    chakra_data = chakra_data_out if chakra_data_out is not None else {}
    hd_gate_activations = hd_gate_activations or {}
    moon_arc = today_positions.get("moon_day_arc")

    for planet_key, pos in today_positions.items():
        if planet_key == "moon_day_arc":
            continue
        natal_sign  = natal_signs.get(planet_key)
        natal_house = natal_houses.get(planet_key)
        if natal_sign is None and natal_house is None:
            # No natal data for this point at all — skip silently, this is a real absence
            continue
        natal_sign  = natal_sign or "unknown"
        natal_house = natal_house if natal_house is not None else "?"
        rx_str = " (retrograde)" if pos.get("retrograde") else ""

        if planet_key == "moon" and moon_arc:
            start_chakra, start_crit = _get_degree_chakra_and_criticality(
                moon_arc["start"]["degree"], moon_arc["start"]["sign"])
            end_chakra, end_crit = _get_degree_chakra_and_criticality(
                moon_arc["end"]["degree"], moon_arc["end"]["sign"])
            chakra_data[planet_key] = {
                "chakra": start_chakra,
                "chakra_end": end_chakra,
                "criticality": start_crit,
                "criticality_end": end_crit,
                "changes_sign": moon_arc.get("changes_sign", False),
            }
            start_str = f"{moon_arc['start']['sign']} {moon_arc['start']['degree']}\u00b0 ({start_chakra} chakra)"
            end_str = f"{moon_arc['end']['sign']} {moon_arc['end']['degree']}\u00b0 ({end_chakra} chakra)"
            shift_note = " The Moon changes SIGN during today, a notable shift." if moon_arc.get("changes_sign") else " The Moon stays within the same sign all day, deepening rather than shifting."
            planet_lines.append(
                f"MOON (moves fast, track across the whole day): "
                f"Starts today at {start_str}. Ends today at {end_str}.{shift_note} "
                f"Natally this person has moon in {natal_sign}, house {natal_house}."
            )
            continue

        chakra, criticality = _get_degree_chakra_and_criticality(pos.get("degree", 0), pos.get("sign", ""))
        chakra_meaning = _CHAKRA_MEANINGS.get(chakra, "")
        chakra_data[planet_key] = {"chakra": chakra, "criticality": criticality}

        crit_str = f" | {criticality}" if criticality else ""

        gate_info = hd_gate_activations.get(planet_key, {})
        gate_str = ""
        if gate_info:
            transit_gate = gate_info.get("transit_gate")
            gate_str = f" Human Design Gate {transit_gate} is active today via this transit."
            if gate_info.get("is_reinforcement"):
                reinforced = ", ".join(gate_info.get("reinforced_natal_planets", []))
                gate_str += f" This REINFORCES a Gate already natally present (carried by natal {reinforced}), amplifying that energy today."
            for completion in gate_info.get("channel_completions", []):
                gate_str += (
                    f" This transit also TEMPORARILY COMPLETES the Channel of {completion['channel']} "
                    f"by connecting with natal {completion['natal_planet']} in Gate {completion['natal_gate']}, "
                    f"activating the {' and '.join(completion['centers'])} centers for today only."
                )

        planet_lines.append(
            f"{planet_key.upper()}: currently transiting {pos.get('sign')} {pos.get('degree')}°{rx_str}. "
            f"Degree-chakra: {chakra} ({chakra_meaning}){crit_str}. "
            f"Natally this person has {planet_key} in {natal_sign}, house {natal_house}.{gate_str}"
        )
    aspects_str = "\n".join(natal_aspects) if natal_aspects else "none calculated"

    return f"""{_DAILY_TRANSIT_VOICE_RULES}

Write a Daily Transit Snapshot for {client_name}.

TODAY'S TRANSITING PLANETS AGAINST THEIR NATAL CHART:
{chr(10).join(planet_lines)}

NATAL ASPECTS (for context only, mention only if directly relevant to a transiting planet):
{aspects_str}

For EACH planet listed above, write 2 to 3 sentences naming:
1. What this transiting planet is doing in the sky right now in this sign
2. What that means landing specifically in THIS person's natal house for that planet
3. Weave in the degree-chakra activation naturally as part of the meaning, using the chakra name and its theme exactly as given. Do not just state the chakra name, integrate what that chakra governs into the sentence about what this transit is asking of them today.
If a criticality note is present (critical degree, karmic degree, anaretic, cardinal/fixed/mutable degree range), name that this is a heightened or threshold degree and let that raise the intensity of the language for that planet only.

SPECIAL RULE FOR THE MOON: The Moon moves through roughly half a degree per hour, so it is not a single static point today, it is a moving arc with a start chakra and an end chakra. Since emotional self-awareness is central to self-love, give the Moon 3 to 4 sentences instead of 2 to 3. Name where the day's emotional weather begins (the starting chakra and what it is asking) and where it shifts to or deepens into by the end of the day (the ending chakra). If it changes sign, name that as a real shift in emotional register across the day, not just a degree change. If it stays in the same sign, name that as the day asking for depth in one emotional theme rather than movement between themes.

HUMAN DESIGN GATE ACTIVATIONS: Where a planet's line above mentions a Human Design Gate, weave that into the writing as practical daily guidance, not abstract theory. If it REINFORCES a natal gate, tell them this is amplifying something already wired into them today, and name what that gate's planet governs for them. If it TEMPORARILY COMPLETES a Channel, tell them this is a one-day-only energetic connection, name the Channel and which centers it activates, and give them one concrete way to use this temporary access today since it will not be there tomorrow. This Gate and Channel data is mechanically calculated and exact. Do not soften it into vague astrology language, name the Gate number and Channel by name directly in the text.

Return ONLY valid JSON with this exact structure. No markdown. No preamble. JSON only:
{{
  "sun": "2-3 sentences",
  "moon": "2-3 sentences",
  "mercury": "2-3 sentences",
  "venus": "2-3 sentences",
  "mars": "2-3 sentences",
  "jupiter": "2-3 sentences",
  "saturn": "2-3 sentences",
  "uranus": "2-3 sentences",
  "neptune": "2-3 sentences",
  "pluto": "2-3 sentences",
  "chiron": "2-3 sentences",
  "northnode": "2-3 sentences",
  "southnode": "2-3 sentences",
  "blackmoonlilith": "2-3 sentences"
}}

Only include keys for planets that appear in the TODAY'S TRANSITING PLANETS list above."""

def _run_daily_transit_generation(payload: dict, job_id: str) -> None:
    try:
        client_d = payload.get("client", {})
        today_positions = payload.get("todayPositions", {})
        natal_signs   = payload.get("natalSigns", {})
        natal_houses  = payload.get("natalHouses", {})
        natal_aspects = payload.get("natalAspects", [])
        natal_planet_positions = payload.get("natalPlanetPositions", [])

        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip() or "this soul"

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")

        # Gate activations calculated mechanically, in code, never left to the AI.
        hd_gate_activations = calculate_daily_hd_gate_activations(today_positions, natal_planet_positions)

        # chakra_data gets filled by _build_daily_transit_prompt as it processes each
        # planet, including the Moon's special start/end arc handling.
        chakra_data = {}
        prompt = _build_daily_transit_prompt(client_name, today_positions, natal_signs, natal_houses, natal_aspects, chakra_data_out=chakra_data, hd_gate_activations=hd_gate_activations)
        claude_body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 3000,
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
        with urllib.request.urlopen(req, timeout=300) as resp:
            claude_data = json.loads(resp.read())

        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        paragraphs = json.loads(result_text)

        # Combine AI prose with code-verified chakra data and HD gate data per planet
        combined = {}
        for planet_key, text in paragraphs.items():
            entry = {
                "text": text,
                "chakra": chakra_data.get(planet_key, {}).get("chakra"),
                "criticality": chakra_data.get(planet_key, {}).get("criticality"),
            }
            if planet_key == "moon":
                entry["chakra_end"] = chakra_data.get(planet_key, {}).get("chakra_end")
                entry["criticality_end"] = chakra_data.get(planet_key, {}).get("criticality_end")
                entry["changes_sign"] = chakra_data.get(planet_key, {}).get("changes_sign", False)

            gate_info = hd_gate_activations.get(planet_key, {})
            if gate_info:
                entry["hd_gate"] = gate_info.get("transit_gate")
                entry["hd_is_reinforcement"] = gate_info.get("is_reinforcement", False)
                entry["hd_reinforced_planets"] = gate_info.get("reinforced_natal_planets", [])
                entry["hd_channel_completions"] = gate_info.get("channel_completions", [])

            combined[planet_key] = entry

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result_json": combined}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


_DEEP_DAILY_VOICE_RULES = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Direct, warm, fierce, precise. Never use em dashes anywhere. Never say medicine, say Rebirth. Never say disorder, condition, or diagnosis. Master numbers never reduced.
DEPTH: This is a paid subscriber reading. Each entry gets its own full body text, 4 to 6 sentences. This is not the free version, do not write a shorter version of it.

STRUCTURE RULE, NO EXCEPTIONS: Each entry has a technical header (the planet, aspect, Human Design Gate, chakra, TCM element) which is given to you separately and already correct. Your job is ONLY the body text underneath. The body text must NEVER repeat or restate the technical header. Never say planet names, aspect names (square, trine, sextile, opposition, conjunction), chakra names, Gate numbers, or TCM terms inside the body text itself. The header already says all of that. Your body text is pure plain language: what to expect today (emotionally, relationally, physically, practically), what it means for this specific person, and what to actually do about it. Write the way a trusted friend with uncanny insight would talk, not the way an astrologer explains a chart. If you catch yourself naming a planet or technical term inside the body text, stop and rewrite that sentence in plain English instead."""


_DEEP_DAILY_MAX_ASPECTS = 12


def _build_deep_daily_prompt(client_name, today_positions, natal_signs, natal_houses, natal_planet_positions, chakra_data_out=None, hd_gate_activations=None, header_map_out=None):
    """
    Builds the prompt for the PAID deep daily reading. This is a completely
    separate function from _build_daily_transit_prompt (the free version) so
    the free reading can never be affected by changes here.
    header_map_out: dict that gets filled with code-built (not AI-built)
    technical headers, keyed by "transit_planet|natal_planet|aspect", so the
    final display never relies on the AI to construct technical labels.
    """
    chakra_data = chakra_data_out if chakra_data_out is not None else {}
    hd_gate_activations = hd_gate_activations or {}
    aspect_header_map = header_map_out if header_map_out is not None else {}

    all_active_aspects = calculate_transit_to_natal_aspects(today_positions, natal_planet_positions)
    active_aspects = all_active_aspects[:_DEEP_DAILY_MAX_ASPECTS]
    remaining_aspects = all_active_aspects[_DEEP_DAILY_MAX_ASPECTS:]

    aspect_lines = []
    for asp in active_aspects:
        t_planet = asp["transit_planet"]
        n_planet = asp["natal_planet"]
        aspect_name = asp["aspect"]
        orb = asp["orb"]

        pos = today_positions.get(t_planet, {})
        chakra, criticality = _get_degree_chakra_and_criticality(pos.get("degree", 0), pos.get("sign", ""))
        chakra_meaning = _CHAKRA_MEANINGS.get(chakra, "")
        tcm_data = get_tcm_for_chakra(chakra)
        tcm_str = ""
        if tcm_data:
            tcm_str = (
                f" In TCM terms, this is the {tcm_data['element']} element, "
                f"activating the {tcm_data['yin_meridian']} (Yin) and {tcm_data['yang_meridian']} (Yang) meridians."
            )

        gate_info = hd_gate_activations.get(t_planet, {})
        gate_str = ""
        if gate_info.get("transit_gate"):
            gate_str = f" This transit is also activating Human Design Gate {gate_info['transit_gate']}."
            if gate_info.get("is_reinforcement"):
                gate_str += f" Reinforcing natal {', '.join(gate_info.get('reinforced_natal_planets', []))}."

        header = f"{t_planet.capitalize()} {aspect_name} natal {n_planet} \u00b7 {chakra}"
        if gate_info.get("transit_gate"):
            header = f"{t_planet.capitalize()} {aspect_name} natal {n_planet} \u00b7 Human Design Gate {gate_info['transit_gate']} \u00b7 {chakra}"
        aspect_header_map[f"{t_planet}|{n_planet}|{aspect_name}"] = header

        aspect_lines.append(
            f"ENTRY KEY: {t_planet}|{n_planet}|{aspect_name}\n"
            f"Transiting {t_planet.upper()} ({pos.get('sign')} {pos.get('degree')}°, {chakra} chakra) is forming a {aspect_name} "
            f"to natal {n_planet} (orb {orb}°).{tcm_str}{gate_str}"
        )
    aspects_block = "\n".join(aspect_lines) if aspect_lines else "No major aspects (within 8 degree orb) are active today."

    remaining_block = ""
    if remaining_aspects:
        remaining_summary = ", ".join(
            f"{a['transit_planet']} {a['aspect']} natal {a['natal_planet']}"
            for a in remaining_aspects
        )
        remaining_block = f"\n\nADDITIONAL ACTIVE ASPECTS (mention briefly in the summary only, do not write full paragraphs for these): {remaining_summary}"

    return f"""{_DEEP_DAILY_VOICE_RULES}

Write the Deep Daily Transit Reading for {client_name}, a paying subscriber.

TODAY'S TIGHTEST, MOST SIGNIFICANT ACTIVE TRANSIT-TO-NATAL ASPECTS (calculated mechanically, exact, sorted tightest orb first):
{aspects_block}{remaining_block}

For EACH of the tightest aspects listed above, write body text only (4 to 6 sentences) covering, in plain language with NO technical terms:
1. What kind of energy or pressure is present today (intensifying, friction/growth, easy flow, awareness through tension, or an opportunity requiring action) described in plain emotional/practical terms, never naming the aspect type itself
2. What this actually means is likely to show up in their day, emotionally, relationally, physically, or practically
3. Any somatic/body sensation this may bring, described plainly (e.g. "you may feel it as tightness in your chest" rather than naming the meridian)
4. One concrete, specific thing to do about it today

Each item above starts with a line "ENTRY KEY: planet|natal_planet|aspect" followed by the technical data for that entry. Use that exact key string in your response so your body text can be matched to the correct entry. Do not alter the key.

Return ONLY valid JSON with this exact structure. No markdown. No preamble. JSON only:
{{
  "aspects": [
    {{
      "key": "mars|Chiron|conjunction",
      "text": "plain language body text only, no jargon, 4 to 6 sentences"
    }}
  ],
  "summary": "2-3 sentence plain-language overview of today's overall theme, zero astrology jargon, zero planet names, zero technical terms. Written as if telling a friend what kind of day to expect and what to keep in mind."
}}

If there are no active aspects today, return an empty aspects array and a summary noting today is a quieter, more internally-focused day."""

def _run_deep_daily_transit_generation(payload: dict, job_id: str) -> None:
    """
    PAID subscriber version of the daily reading. Completely separate from
    _run_daily_transit_generation (the free version) so free users are never
    affected by changes here, and paid logic never accidentally leaks into
    the free tier.
    """
    try:
        client_d = payload.get("client", {})
        today_positions = payload.get("todayPositions", {})
        natal_signs   = payload.get("natalSigns", {})
        natal_houses  = payload.get("natalHouses", {})
        natal_planet_positions = payload.get("natalPlanetPositions", [])

        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip() or "this soul"

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")

        hd_gate_activations = calculate_daily_hd_gate_activations(today_positions, natal_planet_positions)
        chakra_data = {}
        aspect_header_map = {}

        prompt = _build_deep_daily_prompt(
            client_name, today_positions, natal_signs, natal_houses,
            natal_planet_positions, chakra_data_out=chakra_data,
            hd_gate_activations=hd_gate_activations,
            header_map_out=aspect_header_map
        )

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
        with urllib.request.urlopen(req, timeout=400) as resp:
            claude_data = json.loads(resp.read())

        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        parsed = json.loads(result_text)

        # Assemble final aspects using the AI's body text matched to the
        # code-built header map. The AI never constructs headers itself.
        final_aspects = []
        for item in parsed.get("aspects", []):
            ai_key = item.get("key", "")
            header = None
            ai_key_normalized = ai_key.lower().replace(" ", "")
            for map_key, map_header in aspect_header_map.items():
                if map_key.lower().replace(" ", "") == ai_key_normalized:
                    header = map_header
                    break
            if header is None:
                ai_parts = ai_key.split("|")
                if len(ai_parts) >= 2:
                    partial = f"{ai_parts[0]}|{ai_parts[1]}".lower()
                    for map_key, map_header in aspect_header_map.items():
                        if map_key.lower().startswith(partial):
                            header = map_header
                            break
            if header is None:
                header = ai_key

            final_aspects.append({
                "header": header,
                "text": item.get("text", ""),
            })

        combined_result = {
            "aspects": final_aspects,
            "summary": parsed.get("summary", ""),
        }

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result_json": combined_result}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


_WEEKLY_VOICE_RULES = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Direct, warm, fierce, precise. Never use em dashes anywhere. Never say medicine, say Rebirth. Never say disorder, condition, or diagnosis. Master numbers never reduced.
DEPTH: This is a paid subscriber reading. This is a SYNTHESIZED WEEKLY ARC, not seven daily readings stacked together. Write about the week as one unfolding story with a beginning, building, and shape, not a day-by-day list.

ABSOLUTE LANGUAGE RULE, NO EXCEPTIONS: The narrative text must never name planets (Mars, Venus, Mercury, Saturn, Pluto, Uranus, Neptune, Chiron, the Sun, the Moon, the Nodes, Black Moon Lilith), aspect types (square, trine, sextile, opposition, conjunction), chakra names, Human Design Gate numbers, or TCM/meridian terms. The technical data given to you is your reasoning tool, not your vocabulary. Translate everything into plain, predictive, human language: what to expect this week emotionally, relationally, physically, and practically, and what to do about it. Write the way a trusted friend with uncanny insight would talk. If you catch yourself naming a planet or technical term, stop and rewrite that sentence in plain English instead."""


_WEEKLY_MAX_ASPECTS = 8


def _build_weekly_prompt(client_name, start_date_str, scored_arcs, chakra_data_out=None):
    """
    Builds the prompt for the PAID Weekly synthesis reading. Completely
    separate from the Daily and Deep Daily prompt builders, sharing only
    the underlying calculation engines (calculate_aspect_arcs_for_window,
    score_aspect_arcs_for_synthesis), never the prompt/voice logic.
    """
    chakra_data = chakra_data_out if chakra_data_out is not None else {}

    top_arcs = scored_arcs[:_WEEKLY_MAX_ASPECTS]
    remaining_arcs = scored_arcs[_WEEKLY_MAX_ASPECTS:]

    arc_lines = []
    for arc in top_arcs:
        t_planet = arc["transit_planet"]
        n_planet = arc["natal_planet"]
        aspect_name = arc["aspect"]
        enters = arc["enters_orb_date"]
        peak = arc["peak_date"]
        exits = arc["exits_orb_date"]
        duration = arc["duration_days"]
        peak_orb = arc["peak_orb"]

        peak_positions = calculate_planet_positions_for_date(_dt_date.fromisoformat(peak))
        peak_pos = peak_positions.get(t_planet, {})
        peak_lon = peak_pos.get("longitude", 0)
        peak_sign_idx = int(peak_lon // 30) if peak_lon else 0
        peak_sign = _SIGNS_LIST[peak_sign_idx] if peak_lon else "unknown"
        peak_degree = round(peak_lon % 30, 2) if peak_lon else 0

        chakra, criticality = _get_degree_chakra_and_criticality(peak_degree, peak_sign)
        tcm_data = get_tcm_for_chakra(chakra)
        tcm_str = ""
        if tcm_data:
            tcm_str = f" TCM: {tcm_data['element']} element, {tcm_data['yin_meridian']}/{tcm_data['yang_meridian']} meridians."

        arc_lines.append(
            f"Transiting {t_planet.upper()} {aspect_name} natal {n_planet}: active {enters} through {exits} "
            f"({duration} day{'s' if duration != 1 else ''}), peaking {peak} at orb {peak_orb}° "
            f"in {peak_sign} ({chakra} chakra).{tcm_str}"
        )

    arcs_block = "\n".join(arc_lines) if arc_lines else "No major aspect arcs (within 8 degree orb) are active this week."

    remaining_block = ""
    if remaining_arcs:
        remaining_summary = ", ".join(
            f"{a['transit_planet']} {a['aspect']} natal {a['natal_planet']}"
            for a in remaining_arcs[:15]
        )
        remaining_block = f"\n\nADDITIONAL ACTIVE ASPECTS THIS WEEK (mention briefly as background texture only): {remaining_summary}"

    return f"""{_WEEKLY_VOICE_RULES}

Write the Weekly Transit Synthesis for {client_name}, a paying subscriber, for the week of {start_date_str}.

THIS WEEK'S MOST SIGNIFICANT ASPECT ARCS (ranked by duration and planetary speed, calculated mechanically day-by-day, exact):
{arcs_block}{remaining_block}

Write this as ONE FLOWING NARRATIVE of the week, in plain language with zero technical terms anywhere in the prose. Structure it as:
1. Open with the overall shape and energy of the week, what is building and what is releasing, described in plain emotional/practical terms
2. Move through the week's real timeline, naming WHEN things intensify (the peak dates matter, tell the person when to expect the most intensity) and when they ease, all in plain language
3. Weave in body/somatic sensations as plain physical descriptions (e.g. "tightness in your chest"), never naming chakras or meridians
4. Close with the week's core teaching or theme, the one thing this week is actually asking of them

Return ONLY valid JSON with this exact structure. No markdown. No preamble. JSON only:
{{
  "narrative": "the full flowing weekly synthesis, 6 to 10 substantial paragraphs, plain language only, zero jargon, real dates woven in naturally",
  "key_dates": [
    {{"date": "YYYY-MM-DD", "what_peaks": "plain language description of what to expect this specific day, no technical terms"}}
  ],
  "summary": "2-3 sentence plain-language headline of the week, zero jargon"
}}

If there are no significant aspect arcs this week, return an empty key_dates array and write the narrative around the relative quiet, what that quiet makes possible, and what foundational/internal work it supports."""


def _run_weekly_transit_generation(payload: dict, job_id: str) -> None:
    """
    PAID Weekly subscriber reading. Completely separate generation function
    from Daily and Deep Daily, sharing only the calculation engines.
    """
    try:
        client_d = payload.get("client", {})
        start_date_str = payload.get("startDate")
        natal_planet_positions = payload.get("natalPlanetPositions", [])

        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip() or "this soul"

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")
        if not start_date_str:
            raise ValueError("startDate is required")

        start_date = _dt_date.fromisoformat(start_date_str)
        raw_arcs = calculate_aspect_arcs_for_window(start_date, 7, natal_planet_positions)
        scored_arcs = score_aspect_arcs_for_synthesis(raw_arcs, 7)

        chakra_data = {}
        prompt = _build_weekly_prompt(client_name, start_date_str, scored_arcs, chakra_data_out=chakra_data)

        claude_body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 12000,
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
        with urllib.request.urlopen(req, timeout=400) as resp:
            claude_data = json.loads(resp.read())

        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        parsed = json.loads(result_text)

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result_json": parsed}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


_MONTHLY_VOICE_RULES = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Direct, warm, fierce, precise. Never use em dashes anywhere. Never say medicine, say Rebirth. Never say disorder, condition, or diagnosis. Master numbers never reduced.
DEPTH: This is a paid subscriber reading. This is a MONTHLY THEMATIC OVERVIEW, broader than the Weekly synthesis. Write about the chapter this month is writing, the throughline, not individual days or even individual weeks. Name when within the month things peak, but the lens is the whole arc, not the granular week-by-week mechanics.

ABSOLUTE LANGUAGE RULE, NO EXCEPTIONS: The narrative text must never name planets (Mars, Venus, Mercury, Saturn, Pluto, Uranus, Neptune, Chiron, the Sun, the Moon, the Nodes, Black Moon Lilith), aspect types (square, trine, sextile, opposition, conjunction), chakra names, Human Design Gate numbers, or TCM/meridian terms. The technical data given to you is your reasoning tool, not your vocabulary. Translate everything into plain, predictive, human language: what to expect this month emotionally, relationally, physically, and practically, and what to do about it. Write the way a trusted friend with uncanny insight would talk. If you catch yourself naming a planet or technical term, stop and rewrite that sentence in plain English instead."""


_MONTHLY_MAX_ASPECTS = 6


def _build_monthly_prompt(client_name, start_date_str, scored_arcs, chakra_data_out=None):
    """
    Builds the prompt for the PAID Monthly synthesis reading. Completely
    separate from Daily, Deep Daily, and Weekly prompt builders, sharing
    only the underlying calculation engines.
    """
    chakra_data = chakra_data_out if chakra_data_out is not None else {}

    top_arcs = scored_arcs[:_MONTHLY_MAX_ASPECTS]
    remaining_arcs = scored_arcs[_MONTHLY_MAX_ASPECTS:]

    arc_lines = []
    for arc in top_arcs:
        t_planet = arc["transit_planet"]
        n_planet = arc["natal_planet"]
        aspect_name = arc["aspect"]
        enters = arc["enters_orb_date"]
        peak = arc["peak_date"]
        exits = arc["exits_orb_date"]
        duration = arc["duration_days"]
        peak_orb = arc["peak_orb"]

        peak_positions = calculate_planet_positions_for_date(_dt_date.fromisoformat(peak))
        peak_pos = peak_positions.get(t_planet, {})
        peak_lon = peak_pos.get("longitude", 0)
        peak_sign_idx = int(peak_lon // 30) if peak_lon else 0
        peak_sign = _SIGNS_LIST[peak_sign_idx] if peak_lon else "unknown"
        peak_degree = round(peak_lon % 30, 2) if peak_lon else 0

        chakra, criticality = _get_degree_chakra_and_criticality(peak_degree, peak_sign)
        tcm_data = get_tcm_for_chakra(chakra)
        tcm_str = ""
        if tcm_data:
            tcm_str = f" TCM: {tcm_data['element']} element, {tcm_data['yin_meridian']}/{tcm_data['yang_meridian']} meridians."

        arc_lines.append(
            f"Transiting {t_planet.upper()} {aspect_name} natal {n_planet}: active {enters} through {exits} "
            f"({duration} day{'s' if duration != 1 else ''} of this month), peaking {peak} at orb {peak_orb}° "
            f"in {peak_sign} ({chakra} chakra).{tcm_str}"
        )

    arcs_block = "\n".join(arc_lines) if arc_lines else "No major aspect arcs (within 8 degree orb) are active this month."

    remaining_block = ""
    if remaining_arcs:
        remaining_summary = ", ".join(
            f"{a['transit_planet']} {a['aspect']} natal {a['natal_planet']}"
            for a in remaining_arcs[:20]
        )
        remaining_block = f"\n\nADDITIONAL ACTIVE ASPECTS THIS MONTH (mention only if it adds genuine texture, otherwise omit): {remaining_summary}"

    return f"""{_MONTHLY_VOICE_RULES}

Write the Monthly Transit Synthesis for {client_name}, a paying subscriber, for the month beginning {start_date_str}.

THIS MONTH'S MOST SIGNIFICANT, LONGEST-RUNNING ASPECT ARCS (ranked by duration and planetary speed, calculated mechanically day-by-day across the full month, exact):
{arcs_block}{remaining_block}

Write this as ONE FLOWING THEMATIC OVERVIEW of the month, not a list of aspects and not a week-by-week breakdown. Structure it as:
1. Open by naming the single biggest throughline of this month, the chapter title if this month were a chapter in their life story
2. Move through the 2-4 dominant themes the month is carrying, weaving multiple aspects together where they share a common thread rather than treating each in isolation
3. Name when within the month the energy is most concentrated (early, middle, or late month) without getting lost in day-by-day mechanics
4. Weave in chakra and TCM data as the month's overall somatic signature, broad strokes not granular tracking
5. Close with what this month is ultimately building toward or completing

Return ONLY valid JSON with this exact structure. No markdown. No preamble. JSON only:
{{
  "narrative": "the full flowing monthly synthesis, 6 to 10 substantial paragraphs, written as one continuous thematic story of the month",
  "peak_window": {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "description": "what the most concentrated period of the month is about"}},
  "summary": "2-3 sentence headline of the month for someone who only reads one thing"
}}

If there are no significant aspect arcs this month, return a peak_window with null start/end and write the narrative around what a genuinely quiet month makes possible."""


def _run_monthly_transit_generation(payload: dict, job_id: str) -> None:
    """
    PAID Monthly subscriber reading. Completely separate generation function
    from Daily, Deep Daily, and Weekly, sharing only the calculation engines.
    """
    try:
        client_d = payload.get("client", {})
        start_date_str = payload.get("startDate")
        natal_planet_positions = payload.get("natalPlanetPositions", [])

        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip() or "this soul"

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")
        if not start_date_str:
            raise ValueError("startDate is required")

        start_date = _dt_date.fromisoformat(start_date_str)
        raw_arcs = calculate_aspect_arcs_for_window(start_date, 30, natal_planet_positions)
        scored_arcs = score_aspect_arcs_for_synthesis(raw_arcs, 30)

        chakra_data = {}
        prompt = _build_monthly_prompt(client_name, start_date_str, scored_arcs, chakra_data_out=chakra_data)

        claude_body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 12000,
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
        with urllib.request.urlopen(req, timeout=400) as resp:
            claude_data = json.loads(resp.read())

        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        parsed = json.loads(result_text)

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result_json": parsed}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


_THREE_MONTH_VOICE_RULES = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Direct, warm, fierce, precise. Never use em dashes anywhere. Never say medicine, say Rebirth. Never say disorder, condition, or diagnosis. Master numbers never reduced.
DEPTH: This is a paid, pay-per-run projection. This is a FORWARD-LOOKING TIMELINE across 90 days, not a current-moment reading. Frame everything in future tense, as preparation for what is coming, not description of what is happening now.""".strip()


_THREE_MONTH_MAX_ARCS = 8


def _build_three_month_prompt(client_name, start_date_str, scored_arcs):
    """
    Builds the prompt for the PAID, pay-per-run 3-month projection.
    Completely standalone function, fully separate from the 6-month and
    yearly projection builders, sharing only the calculation engines.
    """
    top_arcs = scored_arcs[:_THREE_MONTH_MAX_ARCS]

    arc_lines = []
    for arc in top_arcs:
        t_planet = arc["transit_planet"]
        n_planet = arc["natal_planet"]
        aspect_name = arc["aspect"]
        enters = arc["enters_orb_date"]
        peak = arc["peak_date"]
        exits = arc["exits_orb_date"]
        duration = arc["duration_days"]
        peak_orb = arc["peak_orb"]

        peak_positions = calculate_planet_positions_for_date(_dt_date.fromisoformat(peak))
        peak_pos = peak_positions.get(t_planet, {})
        peak_lon = peak_pos.get("longitude", 0)
        peak_sign_idx = int(peak_lon // 30) if peak_lon else 0
        peak_sign = _SIGNS_LIST[peak_sign_idx] if peak_lon else "unknown"
        peak_degree = round(peak_lon % 30, 2) if peak_lon else 0

        chakra, criticality = _get_degree_chakra_and_criticality(peak_degree, peak_sign)
        tcm_data = get_tcm_for_chakra(chakra)
        tcm_str = f" TCM: {tcm_data['element']} element." if tcm_data else ""

        arc_lines.append(
            f"Transiting {t_planet.upper()} {aspect_name} natal {n_planet}: enters orb {enters}, "
            f"peaks exact on {peak} at orb {peak_orb}° in {peak_sign} ({duration} day window, {chakra} chakra).{tcm_str}"
        )

    arcs_block = "\n".join(arc_lines) if arc_lines else "No major aspect arcs (within 8 degree orb) are projected across this 90 day window."

    return f"""{_THREE_MONTH_VOICE_RULES}

Write the 90 Day Forward Projection for {client_name}, beginning {start_date_str}.

THE MOST SIGNIFICANT ASPECT ARCS PROJECTED ACROSS THE NEXT 90 DAYS (calculated mechanically, exact future planetary positions, sorted by duration and planetary significance):
{arcs_block}

Write this as a forward-looking timeline. Structure it as:
1. Open by naming the overall arc of these 90 days, what this quarter is preparing them for
2. Move through the timeline in chronological order, naming specific future dates when major aspects go exact
3. Distinguish between aspects that are building (early in the window), at their peak (mid-window), and resolving (late window)
4. Close with what becomes possible or what completes by the end of this 90 day window

Return ONLY valid JSON with this exact structure. No markdown. No preamble. JSON only:
{{
  "narrative": "the full forward-looking 90 day timeline, 6 to 9 substantial paragraphs",
  "timeline": [
    {{"date": "YYYY-MM-DD", "headline": "short description of what peaks this date"}}
  ],
  "summary": "2-3 sentence headline of the quarter ahead"
}}

If there are no significant projected arcs, return an empty timeline and write the narrative around what a relatively quiet 90 days makes possible to build or rest into."""


def _run_three_month_projection_generation(payload: dict, job_id: str) -> None:
    """
    PAID, pay-per-run 3-month projection. Fully standalone function,
    independent from the 6-month and yearly projection generators.
    """
    try:
        client_d = payload.get("client", {})
        start_date_str = payload.get("startDate")
        natal_planet_positions = payload.get("natalPlanetPositions", [])

        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip() or "this soul"

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")
        if not start_date_str:
            raise ValueError("startDate is required")

        start_date = _dt_date.fromisoformat(start_date_str)
        raw_arcs = calculate_aspect_arcs_for_window(start_date, 90, natal_planet_positions)
        scored_arcs = score_aspect_arcs_for_synthesis(raw_arcs, 90)

        prompt = _build_three_month_prompt(client_name, start_date_str, scored_arcs)

        claude_body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 10000,
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
        try:
            with urllib.request.urlopen(req, timeout=400) as resp:
                claude_data = json.loads(resp.read())
        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode("utf-8", errors="replace")
            raise ValueError(f"Claude API HTTP {http_err.code}: {error_body}")

        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        try:
            parsed = json.loads(result_text)
        except json.JSONDecodeError as json_err:
            # Surface a snippet around the actual failure point for diagnosis
            err_pos = json_err.pos
            snippet_start = max(0, err_pos - 100)
            snippet_end = min(len(result_text), err_pos + 100)
            snippet = result_text[snippet_start:snippet_end]
            raise ValueError(f"JSON parse failed at char {err_pos}: {json_err.msg}. Context: ...{snippet}...")

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result_json": parsed}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


_SIX_MONTH_VOICE_RULES = """VOICE AND DELIVERY — NON-NEGOTIABLE:
Write in the voice of Christina Stevens. Direct, warm, fierce, precise. Never use em dashes anywhere. Never say medicine, say Rebirth. Never say disorder, condition, or diagnosis. Master numbers never reduced.
DEPTH: This is a paid, pay-per-run projection. This is a FORWARD-LOOKING TIMELINE across 180 days, broader than the 90 day projection. Frame everything in future tense. With a longer window, focus on the major chapters and turning points rather than granular week-to-week movement.""".strip()


_SIX_MONTH_MAX_ARCS = 10


def _build_six_month_prompt(client_name, start_date_str, scored_arcs):
    """
    Builds the prompt for the PAID, pay-per-run 6-month projection.
    Completely standalone function, fully separate from the 3-month and
    yearly projection builders, sharing only the calculation engines.
    """
    top_arcs = scored_arcs[:_SIX_MONTH_MAX_ARCS]

    arc_lines = []
    for arc in top_arcs:
        t_planet = arc["transit_planet"]
        n_planet = arc["natal_planet"]
        aspect_name = arc["aspect"]
        enters = arc["enters_orb_date"]
        peak = arc["peak_date"]
        exits = arc["exits_orb_date"]
        duration = arc["duration_days"]
        peak_orb = arc["peak_orb"]

        peak_positions = calculate_planet_positions_for_date(_dt_date.fromisoformat(peak))
        peak_pos = peak_positions.get(t_planet, {})
        peak_lon = peak_pos.get("longitude", 0)
        peak_sign_idx = int(peak_lon // 30) if peak_lon else 0
        peak_sign = _SIGNS_LIST[peak_sign_idx] if peak_lon else "unknown"
        peak_degree = round(peak_lon % 30, 2) if peak_lon else 0

        chakra, criticality = _get_degree_chakra_and_criticality(peak_degree, peak_sign)
        tcm_data = get_tcm_for_chakra(chakra)
        tcm_str = f" TCM: {tcm_data['element']} element." if tcm_data else ""

        arc_lines.append(
            f"Transiting {t_planet.upper()} {aspect_name} natal {n_planet}: enters orb {enters}, "
            f"peaks exact on {peak} at orb {peak_orb}° in {peak_sign} ({duration} day window, {chakra} chakra).{tcm_str}"
        )

    arcs_block = "\n".join(arc_lines) if arc_lines else "No major aspect arcs (within 8 degree orb) are projected across this 180 day window."

    return f"""{_SIX_MONTH_VOICE_RULES}

Write the 180 Day Forward Projection for {client_name}, beginning {start_date_str}.

THE MOST SIGNIFICANT ASPECT ARCS PROJECTED ACROSS THE NEXT 180 DAYS (calculated mechanically, exact future planetary positions, sorted by duration and planetary significance):
{arcs_block}

Write this as a forward-looking chapter-based timeline. Structure it as:
1. Open by naming the overall arc of these 180 days as a complete chapter, what this half-year is writing
2. Divide the window into 3 to 4 distinct phases or chapters (e.g. opening, building, peak, integration), each with its own real date range and theme
3. Name the single most significant convergence date or window across the whole 180 days
4. Close with what this half-year ultimately completes or makes possible

Return ONLY valid JSON with this exact structure. No markdown. No preamble. JSON only:
{{
  "narrative": "the full forward-looking 180 day chapter-based timeline, 8 to 12 substantial paragraphs",
  "chapters": [
    {{"phase_name": "short name for this phase", "date_range": "Month Day to Month Day", "theme": "1-2 sentence description"}}
  ],
  "peak_convergence": {{"date": "YYYY-MM-DD", "description": "what makes this the most significant date in the 180 day window"}},
  "summary": "2-3 sentence headline of the half-year ahead"
}}

If there are no significant projected arcs, return empty chapters, a null peak_convergence, and write the narrative around what a relatively quiet 180 days makes possible to build or rest into."""


def _run_six_month_projection_generation(payload: dict, job_id: str) -> None:
    """
    PAID, pay-per-run 6-month projection. Fully standalone function,
    independent from the 3-month and yearly projection generators.
    """
    try:
        client_d = payload.get("client", {})
        start_date_str = payload.get("startDate")
        natal_planet_positions = payload.get("natalPlanetPositions", [])

        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip() or "this soul"

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")
        if not start_date_str:
            raise ValueError("startDate is required")

        start_date = _dt_date.fromisoformat(start_date_str)
        raw_arcs = calculate_aspect_arcs_for_window(start_date, 180, natal_planet_positions)
        scored_arcs = score_aspect_arcs_for_synthesis(raw_arcs, 180)

        prompt = _build_six_month_prompt(client_name, start_date_str, scored_arcs)

        claude_body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 12000,
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
        try:
            with urllib.request.urlopen(req, timeout=400) as resp:
                claude_data = json.loads(resp.read())
        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode("utf-8", errors="replace")
            raise ValueError(f"Claude API HTTP {http_err.code}: {error_body}")

        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        parsed = json.loads(result_text)

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result_json": parsed}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


def _run_self_love_language_generation(payload: dict, job_id: str) -> None:
    try:
        client_d = payload.get("client", {})
        astro    = payload.get("astrology", {})
        hd       = payload.get("humanDesign", {})
        num      = payload.get("numerology", {})
        assess   = payload.get("assessment", {})
        hebrew_responses = payload.get("hebrewResponses", [])
 
        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip()
        dob         = client_d.get("dob", "")
        place       = client_d.get("place_of_birth", "")
 
        planet_houses = astro.get("summary", {}).get("planet_houses", {})
        planet_signs  = astro.get("summary", {}).get("planet_signs",  {})
        planet_rx_map = astro.get("summary", {}).get("planet_rx",     {})
        houses_data   = astro.get("birth", {}).get("whole_sign_houses", {})
 
        def get_sign(key):
            return planet_signs.get(key, "unknown")
 
        def get_house(key):
            return planet_houses.get(key, "?")
 
        def get_rx(key):
            return bool(planet_rx_map.get(key, False))
 
        rising_sign  = get_sign("ascendant")
        venus_sign   = get_sign("venus");   venus_house  = get_house("venus")
        moon_sign    = get_sign("moon");    moon_house   = get_house("moon")
        chiron_sign  = get_sign("chiron");  chiron_house = get_house("chiron")
        saturn_sign  = get_sign("saturn");  saturn_house = get_house("saturn"); saturn_rx = get_rx("saturn")
        snode_sign   = get_sign("southnode"); snode_house = get_house("southnode")
        nnode_sign   = get_sign("northnode"); nnode_house = get_house("northnode")
 
        mc_lon = houses_data.get("mc")
        if mc_lon is not None:
            signs_list = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
            mc_sign = signs_list[int(float(mc_lon) / 30.0) % 12]
        else:
            mc_sign = get_sign("midheaven")
 
        sl_score   = assess.get("selfLoveScore", "not completed")
        sl_result  = assess.get("selfLoveResult", "")
        attachment = assess.get("attachmentStyle", "not assessed")
 
        hd_type     = hd.get("type", "unknown")
        hd_authority= hd.get("authority", "unknown")
        hd_profile  = hd.get("profile", "")
        defined_c   = ", ".join(hd.get("definedCenters",   []))
        undefined_c = ", ".join(hd.get("undefinedCenters", []))
        channels    = ", ".join(hd.get("channels", []))
        life_path   = str(num.get("lifePath", {}).get("raw", "unknown"))
 
        career_field = client_d.get("career_field", "not provided")
        career_expr  = client_d.get("career_expression", "not provided")
 
        if hebrew_responses:
            hebrew_felt = "\n".join(
                f"Position {r.get('position', '')} ({r.get('letterName', '')}): \"{r.get('feltResponse', '').strip()}\""
                for r in hebrew_responses if (r.get("feltResponse") or "").strip()
            ) or "not completed"
        else:
            hebrew_felt = "not completed"
 
        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")
 
        def call_claude(prompt, max_tokens=4000):
            body = json.dumps({
                "model": "claude-sonnet-4-6",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
            return data["content"][0]["text"].strip()
 
        text_language = call_claude(_sll_build_prompt_language(
            first_name, venus_sign, venus_house, moon_sign, moon_house,
            rising_sign, sl_score, sl_result, attachment
        ))
        text_stolen = call_claude(_sll_build_prompt_stolen(
            first_name, chiron_sign, chiron_house, saturn_sign, saturn_house,
            saturn_rx, snode_sign, snode_house, moon_sign, moon_house,
            rising_sign, sl_score, attachment, hebrew_felt
        ))
        text_home = call_claude(_sll_build_prompt_home(
            first_name, nnode_sign, nnode_house, mc_sign, venus_sign, venus_house,
            rising_sign, moon_sign, moon_house, hd_type, hd_authority, hd_profile,
            defined_c, undefined_c, channels, life_path, career_field, career_expr
        ))
 
        def text_to_paras(text):
            return "".join(
                f"<p>{p.strip()}</p>"
                for p in text.split("\n\n")
                if p.strip()
            )
 
        paras_language = text_to_paras(text_language)
        paras_stolen   = text_to_paras(text_stolen)
        paras_home     = text_to_paras(text_home)
 
        template_path = Path(__file__).parent / "tcm-system" / "self_love_language_template.html"
        html = template_path.read_text(encoding="utf-8")
 
        html = html.replace("Christina Stevens", client_name)
        html = html.replace("April 9, 1983", dob)
        html = html.replace("Hobbs, NM", place)
        html = html.replace("<!--SLL_SECTION_0_CONTENT-->", paras_language)
        html = html.replace("<!--SLL_SECTION_1_CONTENT-->", paras_stolen)
        html = html.replace("<!--SLL_SECTION_2_CONTENT-->", paras_home)
 
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result": html}
 
    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}
 
 
_SJ_TRIGGER_WORDS = [
    {"id": "rising",   "word": "Emergence",     "planet": "Rising"},
    {"id": "lilith",   "word": "Sovereign",      "planet": "Black Moon Lilith"},
    {"id": "pluto",    "word": "Primordial",     "planet": "Pluto"},
    {"id": "nnode",    "word": "Destiny",        "planet": "North Node"},
    {"id": "saturn",   "word": "Alchemy",        "planet": "Saturn"},
    {"id": "venus",    "word": "Twilight",       "planet": "Venus"},
    {"id": "mars",     "word": "Crimson",        "planet": "Mars"},
    {"id": "pof",      "word": "Synthesis",      "planet": "Part of Fortune"},
    {"id": "uranus",   "word": "Turbulence",     "planet": "Uranus"},
    {"id": "mercury",  "word": "Density",        "planet": "Mercury"},
    {"id": "snode",    "word": "Reincarnation",  "planet": "South Node"},
    {"id": "moon",     "word": "Ghost",          "planet": "Moon"},
    {"id": "vertex",   "word": "Inflection",     "planet": "Vertex"},
    {"id": "sun",      "word": "Zenith",         "planet": "Sun"},
    {"id": "neptune",  "word": "Misthaven",      "planet": "Neptune"},
    {"id": "chiron",   "word": "Paradox",        "planet": "Chiron"},
    {"id": "jupiter",  "word": "Endless",        "planet": "Jupiter"},
    {"id": "mc",       "word": "Vocation",       "planet": "Midheaven"},
]
 
_SJ_PLANET_KEY_MAP = {
    "rising":  "ascendant",
    "lilith":  "blackmoonlilith",
    "pluto":   "pluto",
    "nnode":   "northnode",
    "saturn":  "saturn",
    "venus":   "venus",
    "mars":    "mars",
    "pof":     "partoffortune",
    "uranus":  "uranus",
    "mercury": "mercury",
    "snode":   "southnode",
    "moon":    "moon",
    "vertex":  "vertex",
    "sun":     "sun",
    "neptune": "neptune",
    "chiron":  "chiron",
    "jupiter": "jupiter",
    "mc":      "midheaven",
}
 
_SJ_RADIUS_MAP = {
    "rising": 201, "lilith": 219, "pluto": 210, "nnode": 210, "saturn": 201,
    "venus": 183, "mars": 201, "pof": 201, "uranus": 183, "mercury": 219,
    "snode": 201, "moon": 219, "vertex": 210, "sun": 210, "neptune": 219,
    "chiron": 237, "jupiter": 237, "mc": 219,
}
 
 
def _sj_ecl_to_svg(ecl, asc_ecl):
    diff = ((asc_ecl - ecl) % 360 + 360) % 360
    return (180 + diff) % 360
 
 
def _sj_svg_xy(angle_deg, r, cx=290, cy=290):
    rad = angle_deg * _math.pi / 180
    return cx + r * _math.cos(rad), cy + r * _math.sin(rad)
 
 
def _run_souls_journey_generation(payload: dict, job_id: str) -> None:
    try:
        client_d  = payload.get("client", {})
        astro     = payload.get("astrology", {})
        responses = payload.get("responses", {})

        first_name  = client_d.get("first_name", "")
        last_name   = client_d.get("last_name", "")
        client_name = f"{first_name} {last_name}".strip()
        dob         = client_d.get("dob", "")

        planet_houses = astro.get("summary", {}).get("planet_houses", {})
        planet_signs  = astro.get("summary", {}).get("planet_signs",  {})
        houses_data   = astro.get("birth", {}).get("whole_sign_houses", {})

        asc_ecl = float(houses_data.get("ascendant", 0))

        rising_sign_for_prof = planet_signs.get("ascendant", "Aries")
        cached_today_positions = payload.get("cachedTodayPositions")
        live_prof = get_current_profection_year(dob, rising_sign_for_prof, cached_positions=cached_today_positions) if dob else {}
        prof_house   = live_prof.get("activated_house", 1)
        prof_sign    = live_prof.get("activated_sign", "")
        prof_rulers  = live_prof.get("activated_rulers", [])
        prof_ruler   = ", ".join(r.capitalize() for r in prof_rulers) if prof_rulers else ""
        prof_age     = live_prof.get("age", "")
        prof_transits = live_prof.get("current_transit_positions", {})
        prof_display = f"Age {prof_age} \u00b7 House {prof_house} \u00b7 Time Lord {prof_ruler}" if prof_age else f"House {prof_house} \u00b7 Time Lord {prof_ruler}"

        # Deterministic activation: a planet is active ONLY if it is the Time Lord
        # (rules the profected house's sign) OR it natally tenants the profected house.
        active_planet_ids = set()
        for tw in _SJ_TRIGGER_WORDS:
            pid = tw["id"]
            mapped_key = _SJ_PLANET_KEY_MAP.get(pid, pid)
            house_of_planet = planet_houses.get(mapped_key)
            is_time_lord = mapped_key in prof_rulers
            is_tenant = (house_of_planet == prof_house)
            if is_time_lord or is_tenant:
                active_planet_ids.add(pid)
 
        def get_planet_lon(planet_id):
            key = _SJ_PLANET_KEY_MAP.get(planet_id, planet_id)
            for p in astro.get("birth", {}).get("planet_positions", []):
                pname = p.get("planet", "").lower().replace(" ", "")
                if pname == key:
                    return float(p.get("longitude", 0))
            if planet_id == "rising":
                v = houses_data.get("ascendant")
                return float(v) if v is not None else None
            if planet_id == "mc":
                v = houses_data.get("mc")
                return float(v) if v is not None else None
            if planet_id == "vertex":
                v = houses_data.get("vertex")
                return float(v) if v is not None else None
            return None
 
        def get_sign(planet_id):
            key = _SJ_PLANET_KEY_MAP.get(planet_id, planet_id)
            return planet_signs.get(key, "unknown")
 
        def get_house(planet_id):
            key = _SJ_PLANET_KEY_MAP.get(planet_id, planet_id)
            return planet_houses.get(key, "?")
 
        pp = {}
        for tw in _SJ_TRIGGER_WORDS:
            lon  = get_planet_lon(tw["id"])
            house = get_house(tw["id"])
            act  = tw["id"] in active_planet_ids
            if lon is not None:
                angle = _sj_ecl_to_svg(lon, asc_ecl)
                r     = _SJ_RADIUS_MAP.get(tw["id"], 201)
                x, y  = _sj_svg_xy(angle, r)
                pp[tw["id"]] = {"x": round(x, 1), "y": round(y, 1), "a": round(angle, 1), "r": r, "h": house, "act": act}
            else:
                pp[tw["id"]] = {"x": 290, "y": 290, "a": 0, "r": 201, "h": house, "act": act}
 
        planet_signs_js = {tw["id"]: get_sign(tw["id"]) for tw in _SJ_TRIGGER_WORDS}
 
        trigger_lines = "\n".join(
            f"{tw['word'].upper()} ({tw['planet']}): \"{responses.get(tw['id'], '').strip()}\""
            for tw in _SJ_TRIGGER_WORDS
            if responses.get(tw["id"], "").strip()
        )
 
        chart_summary = "\n".join(
            f"{tw['planet']}: {get_sign(tw['id'])} House {get_house(tw['id'])}"
            for tw in _SJ_TRIGGER_WORDS
        )
 
        active_list_str = ", ".join(sorted(active_planet_ids)) if active_planet_ids else "none"
        inactive_list_str = ", ".join(sorted(set(tw["id"] for tw in _SJ_TRIGGER_WORDS) - active_planet_ids)) or "none"
        time_lord_transit_lines = "\n".join(
            f"{r.capitalize()} is currently transiting {prof_transits.get(r, {}).get('sign', 'unknown')} {prof_transits.get(r, {}).get('degree', '')}\u00b0"
            for r in prof_rulers
        ) or "Time Lord transit position unavailable"

        prompt = f"""You are generating a Soul's Journey Reading for {client_name}, DOB {dob}.
 
This reading follows The Fool through the natal wheel from Rising to Midheaven across 18 planetary positions. The Profection Year Time Lord is {prof_ruler} in House {prof_house} ({prof_sign}).
 
CHART POSITIONS:
{chart_summary}
 
PROFECTION YEAR: Age {prof_age}, House {prof_house}, Sign {prof_sign}, Time Lord {prof_ruler}
CURRENT TIME LORD TRANSIT POSITION:
{time_lord_transit_lines}
 
ACTIVATION IS ALREADY DETERMINED. DO NOT RECALCULATE OR REINTERPRET IT.
These planet ids are ACTIVE this Profection year (they are the Time Lord or natally tenant House {prof_house}): {active_list_str}
These planet ids are NOT ACTIVE this Profection year: {inactive_list_str}
You must follow this activation list exactly. A planet not in the active list MUST be written as a Not This Year stop, regardless of what its felt response says or how significant it seems.
 
TRIGGER WORD FELT RESPONSES:
{trigger_lines}
 
VOICE RULES — NON-NEGOTIABLE:
Write in second person throughout. No em dashes anywhere. Never say medicine, say Rebirth. Never say disorder or condition, say wiring pattern or nervous system design. Be direct, piercing, specific. This is a paid reading. Every activated stop gets 3 to 4 substantial paragraphs.
 
INSTRUCTIONS:
Return ONLY valid JSON with this exact structure. No markdown. No preamble. JSON only:
{{
  "readings": {{
    "rising":   {{"label": "<client felt response copied exactly>", "status": "healed|bridge|shadow|not_activated", "reading": "<paragraphs>"}},
    "lilith":   {{"label": "", "status": "", "reading": ""}},
    "pluto":    {{"label": "", "status": "", "reading": ""}},
    "nnode":    {{"label": "", "status": "", "reading": ""}},
    "saturn":   {{"label": "", "status": "", "reading": ""}},
    "venus":    {{"label": "", "status": "", "reading": ""}},
    "mars":     {{"label": "", "status": "", "reading": ""}},
    "pof":      {{"label": "", "status": "", "reading": ""}},
    "uranus":   {{"label": "", "status": "", "reading": ""}},
    "mercury":  {{"label": "", "status": "", "reading": ""}},
    "snode":    {{"label": "", "status": "", "reading": ""}},
    "moon":     {{"label": "", "status": "", "reading": ""}},
    "vertex":   {{"label": "", "status": "", "reading": ""}},
    "sun":      {{"label": "", "status": "", "reading": ""}},
    "neptune":  {{"label": "", "status": "", "reading": ""}},
    "chiron":   {{"label": "", "status": "", "reading": ""}},
    "jupiter":  {{"label": "", "status": "", "reading": ""}},
    "mc":       {{"label": "", "status": "", "reading": ""}}
  }},
  "closing": "<2 to 3 sentences closing the journey>"
}}
 
Rules:
- label = client's exact felt response copied verbatim from the trigger responses above
- status = healed, bridge, or shadow ONLY for planets in the active list, based on felt response tone. For planets NOT in the active list, status MUST be not_activated regardless of felt response.
- reading = 3 to 4 substantial paragraphs for stops in the active list. For stops NOT in the active list, write 1 short paragraph that clearly states this placement is not active in the current Profection year and explain when it was last or will next be the Time Lord, without implying it is presently driving the year.
- For stops with no felt response, set label to empty string"""
 
        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY is not set")
 
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
        with urllib.request.urlopen(req, timeout=600) as resp:
            claude_data = json.loads(resp.read())
 
        result_text = claude_data["content"][0]["text"].strip()
        result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
        parsed = json.loads(result_text)
 
        readings_data = parsed.get("readings", {})
        active_stops  = list(active_planet_ids)
        closing       = parsed.get("closing", "")
 
        all_stops = []
        for tw in _SJ_TRIGGER_WORDS:
            r       = readings_data.get(tw["id"], {})
            label   = r.get("label", responses.get(tw["id"], ""))
            status  = r.get("status", "not_activated")
            sublabel = f"{get_sign(tw['id'])} \u00b7 House {get_house(tw['id'])}"
            all_stops.append({
                "id":       tw["id"],
                "label":    label,
                "sublabel": sublabel,
                "status":   status,
                "word":     tw["word"],
            })
 
        readings_js = {}
        for tw in _SJ_TRIGGER_WORDS:
            r    = readings_data.get(tw["id"], {})
            text = r.get("reading", "")
            readings_js[tw["id"]] = "".join(
                f"<p>{p.strip()}</p>" for p in text.split("\n") if p.strip()
            )
 
        nty_html = ""
        for tw in _SJ_TRIGGER_WORDS:
            r      = readings_data.get(tw["id"], {})
            felt   = responses.get(tw["id"], "").strip()
            if tw["id"] not in active_planet_ids and felt:
                nty_html += (
                    f'<div style="padding:10px 0;border-bottom:1px solid rgba(212,175,55,0.06);">'
                    f'<div style="font-family:\'Cinzel\',serif;font-size:0.54rem;letter-spacing:0.2em;color:rgba(212,175,55,0.5);text-transform:uppercase;">'
                    f'{tw["word"].upper()} &middot; {tw["planet"]}</div>'
                    f'<div style="font-family:\'Lora\',serif;font-size:0.82rem;color:rgba(245,240,255,0.45);font-style:italic;margin-top:4px;">"{felt}"</div>'
                    f'</div>'
                )
 
        template_path = Path(__file__).parent / "tcm-system" / "souls_journey_template.html"
        html = template_path.read_text(encoding="utf-8")
 
        client_json   = json.dumps({"name": client_name, "dob": dob, "profection": prof_display, "closing": closing}, ensure_ascii=False)
        pp_json       = json.dumps(pp, ensure_ascii=False)
        ps_json       = json.dumps(planet_signs_js, ensure_ascii=False)
        all_json      = json.dumps(all_stops, ensure_ascii=False)
        readings_json = json.dumps(readings_js, ensure_ascii=False)
 
        def replace_block(text, start_marker, end_marker, new_content):
            pattern = re.compile(re.escape(start_marker) + r'.*?' + re.escape(end_marker), re.DOTALL)
            return pattern.sub(f'{start_marker}\n{new_content}\n{end_marker}', text)
 
        html = replace_block(html,
            '// SOULS_JOURNEY_CLIENT_START', '// SOULS_JOURNEY_CLIENT_END',
            f'const CLIENT = {client_json};')
        html = replace_block(html,
            '// SOULS_JOURNEY_ASC_ECL_START', '// SOULS_JOURNEY_ASC_ECL_END',
            f'const ASC_ECL = {asc_ecl};')
        html = replace_block(html,
            '// SOULS_JOURNEY_PP_START', '// SOULS_JOURNEY_PP_END',
            f'const PP = {pp_json};')
        html = replace_block(html,
            '// SOULS_JOURNEY_PLANET_SIGNS_START', '// SOULS_JOURNEY_PLANET_SIGNS_END',
            f'const PLANET_SIGNS = {ps_json};')
        html = replace_block(html,
            '// SOULS_JOURNEY_ALL_START', '// SOULS_JOURNEY_ALL_END',
            f'const ALL = {all_json};')
        html = replace_block(html,
            '// SOULS_JOURNEY_READINGS_START', '// SOULS_JOURNEY_READINGS_END',
            f'const READINGS = {readings_json};')
 
        html = html.replace(
            '<!--NTY_STOPS_START--><!--NTY_STOPS_END-->',
            f'<!--NTY_STOPS_START-->{nty_html}<!--NTY_STOPS_END-->'
        )
        html = html.replace('<!--PROFECTION_DISPLAY-->', prof_display)
 
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
 
        elif path == "/classify-hebrew":
            try:
                questionnaire = payload.get("questionnaire", [])
                l1_positions = payload.get("layer1Positions", [])
                l2_positions = payload.get("layer2Positions", [])
                fib_activations = payload.get("fibonacciActivations", [])
                statuses = _sb_classify_statuses(
                    questionnaire=questionnaire,
                    l1_positions=l1_positions,
                    l2_positions=l2_positions,
                    fib_activations=fib_activations,
                )
                self._send_json(200, {"statuses": statuses})
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})
 
        elif path == "/generate-name-frequency":
            client = payload.get("client", {})
            if not client.get("firstName"):
                self._send_json(400, {"error": "client.firstName is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_name_frequency_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})
 
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
 
        elif path == "/slots":
            try:
                from booking_system import generate_slots_for_month
                year  = int(payload.get("year", 0))
                month = int(payload.get("month", 0))
                if not year or not month:
                    self._send_json(400, {"error": "year and month are required"})
                    return
                slots = generate_slots_for_month(year, month)
                self._send_json(200, {"slots": slots})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
 
        elif path == "/ffs-credit":
            try:
                from booking_system import check_ffs_credit
                email = payload.get("email", "").strip().lower()
                if not email:
                    self._send_json(400, {"error": "email is required"})
                    return
                self._send_json(200, {"hasCredit": check_ffs_credit(email)})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
 
        elif path == "/paypal/create-order":
            try:
                from booking_system import paypal_create_order
                service_name  = payload.get("service_name", "")
                price_cents   = int(payload.get("service_price_cents", 0))
                ffs_applied   = bool(payload.get("ffs_credit_applied", False))
                return_url    = payload.get("return_url")
                cancel_url    = payload.get("cancel_url")
                if not service_name or not price_cents or not return_url or not cancel_url:
                    self._send_json(400, {"error": "Missing required fields"})
                    return
                charged_cents = max(0, price_cents - (7500 if ffs_applied else 0))
                order_id, approval_url = paypal_create_order(
                    charged_cents,
                    f"Phoenix Rebirth | {service_name}",
                    return_url,
                    cancel_url,
                )
                self._send_json(200, {"order_id": order_id, "approval_url": approval_url, "charged_cents": charged_cents})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
 
        elif path == "/paypal/capture-order":
            try:
                from booking_system import paypal_capture_order, save_booking, create_calendar_event, send_confirmation_email
                required = ["order_id","client_name","client_email","service_name","service_price_cents","charged_price_cents"]
                missing = [f for f in required if not payload.get(f)]
                if missing:
                    self._send_json(400, {"error": f"Missing fields: {', '.join(missing)}"})
                    return
                capture_id = paypal_capture_order(payload["order_id"])
                gcal_event_id = None
                meet_link = None
                slot_utc = payload.get("slot_utc")
                if slot_utc:
                    try:
                        gcal_event_id, meet_link = create_calendar_event(
                            slot_utc,
                            int(payload.get("service_duration_minutes", 60)),
                            f"Phoenix Rebirth | {payload['service_name']} — {payload['client_name']}",
                            f"Client: {payload['client_name']}\nEmail: {payload['client_email']}\nService: {payload['service_name']}",
                            payload["client_email"],
                        )
                    except Exception:
                        pass
                booking_row = {**payload, "status": "confirmed", "paypal_capture_id": capture_id, "google_calendar_event_id": gcal_event_id, "google_meet_link": meet_link, "confirmation_email_sent": False}
                save_booking(booking_row)
                try:
                    send_confirmation_email(payload["client_email"], payload["client_name"], payload["service_name"], payload.get("slot_mt_display","Time TBD"), meet_link)
                except Exception:
                    pass
                self._send_json(200, {"status": "confirmed", "meet_link": meet_link, "order_id": payload["order_id"]})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
 
        elif path == "/generate-quiz":
            pdf_url = payload.get("pdf_url", "")
            if not pdf_url:
                self._send_json(400, {"error": "pdf_url is required"})
                return
            try:
                with urllib.request.urlopen(pdf_url, timeout=30) as r:
                    raw_bytes = r.read(500000)
                import io
                try:
                    import pypdf
                    reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
                    text_content = ""
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
                    text_content = text_content[:8000]
                except Exception:
                    import re as _re2
                    raw_str = raw_bytes.decode("latin-1", errors="ignore")
                    parts = _re2.findall(r'BT\s*(.*?)\s*ET', raw_str, _re2.DOTALL)
                    text_content = ' '.join(parts)[:8000]
            except Exception as e:
                self._send_json(500, {"error": f"Could not fetch PDF: {str(e)}"})
                return
            prompt = f"""You are a quiz generator. Read the following content and generate 5 multiple choice questions to test comprehension. Each question must have exactly 4 options (A, B, C, D) and one correct answer. Return ONLY a JSON array with this exact structure, no other text:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0
  }}
]
The 'correct' field is the zero-based index of the correct option.
 
Content:
{text_content}"""
            api_key = os.environ.get("CLAUDE_API_KEY", "")
            if not api_key:
                self._send_json(500, {"error": "CLAUDE_API_KEY not set"})
                return
            claude_body = json.dumps({
                "model": "claude-sonnet-4-6",
                "max_tokens": 2000,
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
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    claude_data = json.loads(resp.read())
                result_text = claude_data["content"][0]["text"].strip()
                result_text = re.sub(r'^```\w*\n?', '', result_text).rstrip('`').strip()
                match = re.search(r'\[.*\]', result_text, re.DOTALL)
                questions = json.loads(match.group(0)) if match else []
                self._send_json(200, {"questions": questions})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
 
        elif path == "/weekly-guide-pdf":
            try:
                if not payload:
                    self._send_json(400, {"error": "No payload"})
                    return
                from weekly_guide_pdf import build_guide_pdf
                pdf_bytes = build_guide_pdf(payload)
                pdf_b64   = base64.b64encode(pdf_bytes).decode("utf-8")
                client_name = payload.get("client_name", "client")
                week_num    = int(payload.get("week_number", 2))
                safe_name   = client_name.replace(" ", "_").lower()
                filename    = f"week{week_num}_guide_{safe_name}.pdf"
                self._send_json(200, {"ok": True, "pdf_base64": pdf_b64, "filename": filename})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
 
        elif path == "/transformation-pdf":
            try:
                if not payload:
                    self._send_json(400, {"error": "No payload"})
                    return
                pdf_type    = payload.get("pdf_type", "")
                client_name = payload.get("client_name", "Client")
                if pdf_type not in ("week1_baseline", "week5_response", "comparison"):
                    self._send_json(400, {"error": f"Unknown pdf_type: {pdf_type}"})
                    return
                pdf_bytes = generate_transformation_pdf(payload)
                pdf_b64   = base64.b64encode(pdf_bytes).decode("utf-8")
                safe_name = client_name.replace(" ", "_").lower()
                if pdf_type == "week1_baseline":
                    filename = f"hf_week1_{safe_name}.pdf"
                elif pdf_type == "week5_response":
                    filename = f"hf_week5_{safe_name}.pdf"
                else:
                    filename = f"hf_comparison_{safe_name}.pdf"
                self._send_json(200, {"ok": True, "pdf_base64": pdf_b64, "filename": filename})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/test-aspect-arcs":
            try:
                from datetime import date as _date
                start_date_str = payload.get("startDate")
                num_days = int(payload.get("numDays", 7))
                natal_planet_positions = payload.get("natalPlanetPositions", [])
                if not start_date_str:
                    self._send_json(400, {"error": "startDate is required"})
                    return
                start_date = _date.fromisoformat(start_date_str)
                result = calculate_aspect_arcs_for_window(start_date, num_days, natal_planet_positions)
                self._send_json(200, {"arcs": result, "count": len(result)})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/test-transit-aspects":
            try:
                today_positions = payload.get("todayPositions", {})
                natal_planet_positions = payload.get("natalPlanetPositions", [])
                result = calculate_transit_to_natal_aspects(today_positions, natal_planet_positions)
                self._send_json(200, {"aspects": result, "count": len(result)})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/calculate-daily-transits":
            try:
                result = calculate_todays_planet_positions()
                self._send_json(200, result)
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/hd-gate-lookup":
            try:
                longitude = payload.get("longitude")
                natal_planet_positions = payload.get("natalPlanetPositions", [])
                if longitude is None:
                    self._send_json(400, {"error": "longitude is required"})
                    return
                single_position = {"_lookup": {"longitude": float(longitude)}}
                result = calculate_daily_hd_gate_activations(single_position, natal_planet_positions)
                self._send_json(200, result.get("_lookup", {}))
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/health-tab-daily-overlay":
            try:
                today_positions = payload.get("todayPositions", {})
                natal_planet_positions = payload.get("natalPlanetPositions", [])
                if not today_positions:
                    self._send_json(400, {"error": "todayPositions is required"})
                    return

                hd_gate_activations = calculate_daily_hd_gate_activations(today_positions, natal_planet_positions)

                overlay = {}
                for planet_key, pos in today_positions.items():
                    if planet_key == "moon_day_arc":
                        continue
                    chakra, criticality = _get_degree_chakra_and_criticality(
                        pos.get("degree", 0), pos.get("sign", "")
                    )
                    gate_info = hd_gate_activations.get(planet_key, {})
                    overlay[planet_key] = {
                        "chakra": chakra,
                        "chakra_meaning": _CHAKRA_MEANINGS.get(chakra, ""),
                        "criticality": criticality,
                        "hd_gate": gate_info.get("transit_gate"),
                        "hd_is_reinforcement": gate_info.get("is_reinforcement", False),
                        "hd_reinforced_planets": gate_info.get("reinforced_natal_planets", []),
                        "hd_channel_completions": gate_info.get("channel_completions", []),
                    }

                self._send_json(200, {"date": today_positions.get("date"), "overlay": overlay})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

        elif path == "/generate-daily-transit-reading":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            if not payload.get("todayPositions"):
                self._send_json(400, {"error": "todayPositions is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_daily_transit_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/generate-six-month-projection":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            if not payload.get("startDate"):
                self._send_json(400, {"error": "startDate is required"})
                return
            if not payload.get("natalPlanetPositions"):
                self._send_json(400, {"error": "natalPlanetPositions is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_six_month_projection_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/generate-three-month-projection":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            if not payload.get("startDate"):
                self._send_json(400, {"error": "startDate is required"})
                return
            if not payload.get("natalPlanetPositions"):
                self._send_json(400, {"error": "natalPlanetPositions is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_three_month_projection_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/generate-monthly-transit-reading":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            if not payload.get("startDate"):
                self._send_json(400, {"error": "startDate is required"})
                return
            if not payload.get("natalPlanetPositions"):
                self._send_json(400, {"error": "natalPlanetPositions is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_monthly_transit_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/generate-weekly-transit-reading":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            if not payload.get("startDate"):
                self._send_json(400, {"error": "startDate is required"})
                return
            if not payload.get("natalPlanetPositions"):
                self._send_json(400, {"error": "natalPlanetPositions is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_weekly_transit_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/generate-deep-daily-transit-reading":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            if not payload.get("todayPositions"):
                self._send_json(400, {"error": "todayPositions is required"})
                return
            if not payload.get("natalPlanetPositions"):
                self._send_json(400, {"error": "natalPlanetPositions is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_deep_daily_transit_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/generate-self-love-language":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_self_love_language_generation, args=(payload, job_id), daemon=True)
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/generate-souls-journey":
            client = payload.get("client", {})
            if not client.get("first_name"):
                self._send_json(400, {"error": "client.first_name is required"})
                return
            if not payload.get("responses"):
                self._send_json(400, {"error": "responses is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(target=_run_souls_journey_generation, args=(payload, job_id), daemon=True)
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
 
