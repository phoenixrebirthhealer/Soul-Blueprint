import argparse
import json
import os
import re
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


def _run_claude_generation(prompt: str, job_id: str) -> None:
    """Background thread: call Claude API and store result in job dict."""
    try:
        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("Claude API key is not configured on the server. Add CLAUDE_API_KEY to Railway variables.")

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

def _call_claude(prompt: str, max_tokens: int = 4096) -> str:
    api_key = os.environ.get("CLAUDE_API_KEY", "")
    if not api_key:
        raise ValueError("Claude API key not set. Add CLAUDE_API_KEY to Railway variables.")
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

            raw = _call_claude(prompt, max_tokens=4096)
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

        raw_j = _call_claude(journey_prompt, max_tokens=4096)
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
                      f'<!--NAMFREQ_CONTENT_START-->\n{chr(10).join(name_sections_html)}\n{journey_section_html}\n<!--NAMFREQ_CONTENT_END-->', html)
        html = html.replace('<!--NAMFREQ_FOOTER-->',
                            f'Phoenix Rebirth · Name Frequency Reading · {client_name} · Proprietary · 2026')

        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "complete", "result": html}

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[job_id] = {"status": "failed", "error": str(exc)}


# ============================================================
# SOUL BLUEPRINT TIER 1 -- GENERATION ENGINE
# Phoenix Rebirth | Christina Stevens | Proprietary
# ============================================================

_SB_CAREER_RULERSHIP = {
    "Aries":["Military and Defense","Sports and Athletics","Engineering and Technology","Government and Law"],
    "Taurus":["Business and Finance","Real Estate and Construction","Arts and Creative Expression","Hospitality and Service"],
    "Gemini":["Communications and Media","Education and Teaching","Sales and Marketing","Science and Research"],
    "Cancer":["Healthcare and Healing","Social Work and Advocacy","Hospitality and Service","Education and Teaching"],
    "Leo":["Arts and Creative Expression","Communications and Media","Government and Law","Education and Teaching"],
    "Virgo":["Healthcare and Healing","Science and Research","Social Work and Advocacy","Business and Finance"],
    "Libra":["Government and Law","Arts and Creative Expression","Communications and Media","Social Work and Advocacy"],
    "Scorpio":["Metaphysical and Spiritual Work","Business and Finance","Healthcare and Healing","Science and Research"],
    "Sagittarius":["Education and Teaching","Government and Law","Communications and Media","Metaphysical and Spiritual Work"],
    "Capricorn":["Government and Law","Business and Finance","Engineering and Technology","Real Estate and Construction"],
    "Aquarius":["Engineering and Technology","Science and Research","Social Work and Advocacy","Communications and Media"],
    "Pisces":["Metaphysical and Spiritual Work","Healthcare and Healing","Arts and Creative Expression","Social Work and Advocacy"],
}

_SB_CAREER_EXPR = {
    "Aries":["Leading","Building","Disrupting"],
    "Taurus":["Building","Creating","Service"],
    "Gemini":["Teaching","Writing","Communicating"],
    "Cancer":["Counseling","Caregiving","Supporting"],
    "Leo":["Performing","Leading","Creating"],
    "Virgo":["Analysis","Service","Healing"],
    "Libra":["Counseling","Creating","Leading"],
    "Scorpio":["Transforming","Healing","Analysis","Research"],
    "Sagittarius":["Teaching","Writing","Leading"],
    "Capricorn":["Building","Leading","Analysis"],
    "Aquarius":["Research","Disrupting","Teaching"],
    "Pisces":["Healing","Performing","Counseling","Creating"],
}

_SB_HEB_POS_REF = {
    0:{"name":"The Fool","element":"Void","bridge":False,"shadow":"Terror. Paralysis. Refusal of the leap. The soul that cannot step off the edge because it has forgotten what is on the other side.","healed":"Pure potential. Anticipation. The soul that has leaped before and KNOWS. The lump in the throat is recognition not fear. The center from which all journeys begin.","medicine":None},
    1:{"name":"Aleph","element":"Air","bridge":False,"shadow":"Voicelessness. The strength that cannot speak. The leader who has been silenced. The Ox without a field to plow.","healed":"The silent letter. The breath before sound. Pure strength held in complete stillness before expression. Tears as the recognition of origin, where all sound begins.","medicine":None},
    2:{"name":"Bet","element":"Earth","bridge":False,"shadow":"Imprisonment. The container that traps rather than protects. The house that became a cage. The inside that has no outside.","healed":"The House. Sacred containment. The calm of true safety. The serenity of having a home base that cannot be taken. The first sound of creation held in stillness.","medicine":None},
    3:{"name":"Gimel","element":"Fire","bridge":True,"shadow":"The burden of carrying what is not yours. The camel overloaded. The bridge that collapses under too much weight. Movement without direction.","healed":"The Camel. Effortless movement between worlds. Carrying exactly what is needed across the wilderness. The bridge that holds because it was built for the journey.","medicine":"Bridge position: What is being protected and is that protection serving the journey or slowing it? Determined by chart specifics."},
    4:{"name":"Dalet","element":"Earth","bridge":False,"shadow":"Airy. Floaty. The threshold that cannot be crossed. The door that exists but leads nowhere. Disconnection from the physical at the exact moment embodiment is required.","healed":"The Door. Grounded presence at the threshold. The calm clarity of knowing exactly which passage to take and when. The doorway fully inhabited.","medicine":"Look for: disconnection from body in Human Design definition, floating Pisces or Neptune emphasis in Astrology. Rebirth involves grounding practices specific to this person's chart before threshold crossing is possible."},
    5:{"name":"Heh","element":"Air","bridge":False,"shadow":"The window that is shut. The breath held. Revelation blocked. The divine breath that cannot move through because the opening is sealed by fear or control.","healed":"The Window. Presence as the direct experience of the divine breath moving through. The opening fully inhabited. Revelation received without filtering.","medicine":None},
    6:{"name":"Vav","element":"Earth","bridge":False,"shadow":"Pressure. The nail driven too deep. The connector that becomes a burden. The weight of holding heaven and earth together when neither side is holding you back.","healed":"The Hook. The Nail. The sacred AND. The effortless connection between above and below. The one who holds things together because it is their nature not their obligation.","medicine":"Look for: caretaker patterns in Self-Love Assessment particularly Q8 and Q20, 6 line profile in Human Design, heavy 6th house emphasis in Astrology. Rebirth involves releasing the weight of connection that was never this person's to carry alone."},
    7:{"name":"Zayin","element":"Air","bridge":False,"shadow":"The sword turned on the self. Discernment weaponized into self-destruction. The cutting that cannot stop. Judgment without mercy.","healed":"The Sword of sacred discernment. The direct experience of the divine through the precision of true seeing. Divinity felt as the sword cuts cleanly through to truth.","medicine":None},
    8:{"name":"Chet","element":"Water","bridge":False,"shadow":"The fence that imprisons. The enclosure that suffocates. The protection that became a prison. Life force trapped inside a boundary that was meant to protect but now restricts.","healed":"CHAI. Life itself experienced as source. The sacred enclosure that allows life to flourish. The direct felt sense of the life force that animates everything.","medicine":None},
    9:{"name":"Tet","element":"Earth","bridge":False,"shadow":"Intensity. Pain. The serpent coiled too tight. The hidden good that cannot emerge because the containment has become suffering.","healed":"The hidden goodness that emerges through containment and transformation. The serpent that rises when the coiling is complete. The basket that releases what it has been transforming at exactly the right moment.","medicine":"Look for: Scorpio or Pluto intensity in Astrology, emotional intensity scores in Self-Love Assessment, karmic debt 13 or 16, Generator or Manifesting Generator frustration in Human Design. Rebirth involves learning to distinguish between transformative containment and unnecessary suffering."},
    10:{"name":"Yod","element":"Fire","bridge":False,"shadow":"The divine spark suppressed. The smallest letter made to feel worthless. The seed point of all creation told it is nothing.","healed":"The divine spark experienced directly as bliss. The smallest letter containing the greatest power felt in the body as joy. The Yod within every letter recognizing itself.","medicine":None},
    11:{"name":"Kaf","element":"Fire","bridge":False,"shadow":"The closed palm. The crown too heavy to wear. The capacity to receive turned into inability. Self-loathing underneath the refusal to be held.","healed":"Power as the direct experience of the open palm fully activated. The crown worn with ease. The capacity to receive AND to hold simultaneously. Power in complete service.","medicine":None},
    12:{"name":"Lamed","element":"Air","bridge":False,"shadow":"Hatred. Loathing. The teacher who was told their wisdom was wrong. The student punished for reaching too high. The tallest letter forced to bow.","healed":"The tallest Hebrew letter. The teacher and student simultaneously. The aspiration that reaches toward heaven without apology. The staff that guides without dominating.","medicine":"Look for: wounds around intelligence or wisdom in Self-Love Assessment Q6 and Q17, Chiron in Gemini or 3rd house in Astrology, 12th line in Human Design profile, karmic debt 13. Rebirth involves reclaiming the right to reach, to teach, to learn, to aspire, without shame or apology."},
    13:{"name":"Mem","element":"Water","bridge":True,"shadow":"The waters that drown. The unconscious that overwhelms. The womb that cannot release. The hidden wisdom sealed so tightly it becomes suffocating depth.","healed":"The primordial waters. The womb of all creation. The unconscious depths that hold infinite wisdom. The darkness that is generative not destructive.","medicine":"Bridge position: Whether the depth feels generative or drowning is determined by chart specifics, particularly water emphasis in Astrology and emotional regulation scores in Self-Love Assessment."},
    14:{"name":"Nun","element":"Water","bridge":False,"shadow":"The fish that has given up swimming. The seed that refuses to germinate. Faithlessness in the deep. The soul that stops moving through the waters and sinks.","healed":"Patience as the direct experience of faithful movement through the deep. The fish that knows the waters. The seed that trusts its timing. The soul that moves steadily without forcing.","medicine":None},
    15:{"name":"Samech","element":"Fire","bridge":False,"shadow":"The circle that imprisons. The cycle that has no exit. The support withdrawn. The prop removed at the critical moment. Endless repetition without evolution.","healed":"Nothing and Space as the direct experience of the perfect circle. The sacred emptiness of the divine support that needs no beginning or end. The spaciousness of being fully held without requiring anything in return.","medicine":None},
    16:{"name":"Ayin","element":"Earth","bridge":False,"shadow":"The eye that cannot see. The spring that has dried. The inner vision blocked or suppressed until perception fails entirely. Dry. Heat. Death.","healed":"Grace as the direct experience of the inner eye fully open. The spring flowing freely. Perception of the divine moving through without obstruction. The eye that sees grace in everything.","medicine":None},
    17:{"name":"Peh","element":"Air","bridge":False,"shadow":"The mouth that has been silenced, weaponized, or forced to speak falsely until the body rejects the word entirely. The voice that creates death instead of life.","healed":"The Mouth. The word that creates reality. The voice that vibrates matter into form. The authentic expression that brings things to life.","medicine":"Look for: professional singers, teachers, healers with voice wounds. Q6 in Self-Love Assessment, Gemini or Mercury wounds in Astrology, Throat center definition in Human Design, karmic debt 19. Rebirth involves the gradual reclamation of authentic voice, starting with speaking truth in safe containers before expanding to public expression."},
    18:{"name":"Tzadi","element":"Water","bridge":False,"shadow":"The empath who absorbs everything they pull from the deep without releasing it. The righteous one crushed under the weight of the community's shadows.","healed":"The Tzaddik. The righteous one who pulls hidden things from the deep AND releases them cleanly. The anchor who holds the community without carrying the community's weight in their own body.","medicine":"Look for: empath indicators across all systems, Q18 and Q19 in Self-Love Assessment, open Solar Plexus or Spleen in Human Design, Pisces or Neptune overwhelm in Astrology. Rebirth involves learning the difference between pulling from the deep and keeping what was pulled."},
    19:{"name":"Qof","element":"Earth","bridge":True,"shadow":"The cycle that burns rather than returns. The unconscious that ignites rather than processes. Temperament as uncontrolled fire at the threshold between cycles.","healed":"The sun on the horizon between worlds. The cycle that returns having been fully processed. Temperance as the mastery of the fire between cycles. The blazing that illuminates rather than destroys.","medicine":"Bridge position: Whether the blaze is controlled or consuming is determined by chart specifics, particularly fire emphasis in Astrology and emotional regulation in Self-Love Assessment."},
    20:{"name":"Resh","element":"Air","bridge":False,"shadow":"The head turned away. The leader who refuses to lead. The beginning that cannot begin. The face looking backward instead of forward.","healed":"Resonance as the direct experience of consciousness fully aligned with its own beginning. The head in perfect harmony with itself. The leader whose very presence creates resonance in everything around them.","medicine":None},
    21:{"name":"Shin","element":"Fire","bridge":False,"shadow":"Ego. The divine fire burning for itself. The transformation that serves the transformer rather than the transformation.","healed":"Love as the direct experience of the divine fire in its fully surrendered form. The fire that burns in complete service to creation. The Phoenix flame that rises because love requires it not because ego demands it.","medicine":None},
    22:{"name":"Tav","element":"Earth","bridge":False,"shadow":"Ego. The seal used as personal stamp rather than divine completion. The I AM that tips into I AM MORE THAN. The signature of self-importance rather than the signature of truth.","healed":"The Seal. The divine signature on all of creation. The I AM in complete alignment with truth. The completion that contains and honors everything that came before it without needing to own it.","medicine":"Look for: ego protection patterns in Self-Love Assessment particularly Q4 and Q15, Leo or Sun prominence in Astrology, Manifestor type in Human Design, master number 22 in Numerology. Rebirth involves the distinction between full authentic self-expression (healed Tav) and self-importance (shadow Tav)."},
}

_SB_VOICE_RULES = """VOICE AND DELIVERY - NON-NEGOTIABLE:
- Write in the voice of Christina Stevens. She is a 5'5\" 113 pound force of nature who cusses like a sailor, a construction worker, and a truck driver all at once. She is unfiltered, direct, warm, fierce, and funny. She never softens truth to make it comfortable. She speaks to clients like a best friend who happens to be the most accurate soul reader alive.
- Profanity is not just permitted it is expected when it serves truth. Fuck, shit, hell, ass, damn are all on the table when they land harder than their sanitized versions. Use them when they are the most accurate word available.
- Never use spiritual jargon when a real human word works better. Say what it actually is.
- Direct and unflinching. Do not sanitize. Do not soften. If the truth has an edge let it have the edge.
- Always speak TO the person. Never AT them.
- A Force in Extra Small energy. Big truth. Small packaging. Maximum impact.
- Never coddle. Never diagnose. Never shame. These three override everything else.
- Before you inform, you recognize. Before you analyze, you witness.
- Every word must pass one test: Would this person feel SEEN? Not informed. SEEN.
- The opening paragraph must produce a physical response - lump in throat, tears, held breath.
- The Rebirth is never a list. It is a direction. A felt sense of walking forward.
- The Phoenix does not rise because it has to. It rises because it was always going to.

LANGUAGE RULES - ABSOLUTE:
- NEVER use the word \"medicine\" anywhere. ALWAYS use \"Rebirth\" instead.
- NEVER say \"Your Life Path number is X\" - open with what the original number demands of this specific person.
- NEVER use the words disorder, condition, or diagnosis.
- ALWAYS use: wiring pattern, neurological architecture, soul chosen processing difference, nervous system design.
- Master numbers are NEVER reduced. Ever. Under any circumstances.
- The Soul Blueprint system activates Rebirths. It does not give advice.
- NOT NOW is never changed to No or Decline. The door stays open always.
- NEVER use em dashes anywhere in the reading. Not once. Not ever. Use a comma, a period, or a new sentence instead. Em dashes are absolutely forbidden in every part of every output."""


def _sb_build_hebrew_block(hebrew: dict, questionnaire: list) -> dict:
    NAME_MAP = {0:"The Fool",1:"Aleph",2:"Bet",3:"Gimel",4:"Dalet",5:"Heh",6:"Vav",7:"Zayin",8:"Chet",9:"Tet",10:"Yod",11:"Kaf",12:"Lamed",13:"Mem",14:"Nun",15:"Samech",16:"Ayin",17:"Peh",18:"Tzadi",19:"Qof",20:"Resh",21:"Shin",22:"Tav"}
    ELEM_MAP = {0:"Void",1:"Air",2:"Earth",3:"Fire",4:"Earth",5:"Air",6:"Earth",7:"Air",8:"Water",9:"Earth",10:"Fire",11:"Fire",12:"Air",13:"Water",14:"Water",15:"Fire",16:"Earth",17:"Air",18:"Water",19:"Earth",20:"Air",21:"Fire",22:"Earth"}
    statuses = hebrew.get("positionStatuses", {}) if hebrew else {}
    l1 = hebrew.get("layer1Positions", []) if hebrew else []
    l2 = hebrew.get("layer2Positions", []) if hebrew else []
    fib_set = set(hebrew.get("fibonacciActivations", [])) if hebrew else set()
    conv_set = set(hebrew.get("convergencePoints", [])) if hebrew else set()
    q = questionnaire or []
    positions = {}
    for i in range(23):
        l1c = sum(1 for p in l1 if int(p.get("position", -1)) == i)
        l2c = sum(1 for p in l2 if int(p.get("position", -1)) == i)
        is_fib = i in fib_set
        is_conv = i in conv_set
        q_item = None
        if i > 0:
            for r in q:
                if int(r.get("position", 0)) == i:
                    q_item = r
                    break
        felt = "center point - derived from overall pattern" if i == 0 else (q_item.get("feltResponse", "").strip() if q_item else "no response")
        status = statuses.get(str(i), statuses.get(i, "not_activated"))
        positions[i] = {
            "name": NAME_MAP[i], "element": ELEM_MAP[i], "status": status,
            "nameLetters": l1c, "birthDate": l2c, "fibonacci": is_fib, "convergence": is_conv,
            "totalActivations": l1c + l2c + (1 if is_fib else 0), "felt": felt,
        }
    return positions


def _sb_build_pre_analysis(data: dict) -> str:
    astro = data.get("astrology", {})
    heb = data.get("hebrew", {})
    num = data.get("numerology", {})
    ass = data.get("assessment", {})
    hd = data.get("humanDesign", {})
    major_aspects = astro.get("majorAspects", [])
    return f"""INTERNAL SCAFFOLDING - DO NOT OUTPUT ANY OF THIS ANALYSIS IN YOUR RESPONSE.
Run all four pre-analyses internally before writing a single word. The analysis itself is invisible.
Only the reading prose that results from this analysis appears in your output.

PRE-ANALYSIS 0 - SUN ASSESSMENT (internal only, never output):
Check the majorAspects array for any aspect that contains "sun" (case-insensitive).
Sun aspects from data: {json.dumps(major_aspects)}
If sun appears in any aspect: Identity fusion risk present. Excavate sovereign identity before naming challenges. Establish WHO THEY ARE first.
If sun does not appear in any aspect: Sovereign identity is architecturally separate from all experiences. This person HAS their experiences. They are NOT their experiences. Name this explicitly and early.

PRE-ANALYSIS 1 - WEIGHT IDENTIFICATION (internal only, never output):
Identify the four wounds. Weave them into the opening position. Do not list them.
1. Self-Love score gap = relational wound
   Score: {ass.get("selfLoveScore")} | Range: {ass.get("scoreRange")}
   Attachment dominant: {ass.get("attachmentStyle")}
   Bypass detected: {ass.get("bypassDetected")}
2. Chart ruler, Rising, Moon, MC tension = identity wound
   Chart ruler: {astro.get("chartRuler", "not entered")}
   Rising: {astro.get("rising", "not entered")}
   Moon: {astro.get("moon", "not entered")}
   MC: {astro.get("midheaven", "not entered")}
3. Life Path raw number demand = mission wound
   Life Path raw: {num.get("lifePath", {}).get("raw")} | reduced: {num.get("lifePath", {}).get("reduced")}
4. Shadow positions on Metatron map = frequency wound
   Convergence points: {json.dumps(heb.get("convergencePoints", []))}
   Elemental wounds: {json.dumps(heb.get("elementalWounds", []))}
Synthesize all four into ONE opening position paragraph. Weave. Do not list.

PRE-ANALYSIS 2 - ELEMENTAL CROSS-REFERENCE (internal only, never output):
Hebrew dominant element: {heb.get("dominantElement")}
Hebrew elemental wounds (zero activations): {json.dumps(heb.get("elementalWounds", []))}
Rising sign element: {astro.get("risingElement", "not entered")}
Undefined HD centers: {json.dumps(hd.get("undefinedCenters", []))}
Karmic debts: {json.dumps(num.get("karmicDebts", []))} (13=Earth, 14=Air+Water, 16=Fire, 19=Air)
Synthesize into: PRIMARY elemental wound + PRIMARY elemental gift + elemental TENSION + elemental REBIRTH
Use as invisible structural backbone. Weave through the reading. Never name it as a header.

PRE-ANALYSIS 3 - COMMUNICATION STYLE (internal only, never output):
HD Type: {hd.get("type")}
Dominant element: {heb.get("dominantElement")}
Self-Love score: {ass.get("selfLoveScore")}
HD Type determines directness level. Hebrew dominant element sets tonal temperature. Self-Love score determines how quickly to go deep versus building safety first.

AGAIN: DO NOT PRINT ANY OF THE ABOVE ANALYSIS IN YOUR RESPONSE. It is invisible scaffolding only.
Your response begins with [JOURNEY_MAP] and nothing else comes before it."""


def _sb_build_prompt(data: dict) -> str:
    client = data.get("client", {})
    astro = data.get("astrology", {})
    hd = data.get("humanDesign", {})
    num = data.get("numerology", {})
    heb = data.get("hebrew", {})
    ass = data.get("assessment", {})
    current_year = _datetime.now().year

    q_list = ass.get("hebrewQuestionnaire", [])
    if q_list:
        q_lines = "\n".join([f"Position {r.get('position','')} ({r.get('letterName','')}): {r.get('feltResponse','')}" for r in q_list])
    else:
        q_lines = "not completed"

    heb_block = _sb_build_hebrew_block(heb, q_list)
    pre = _sb_build_pre_analysis(data)

    def p(key): return astro.get(key) or "not entered"
    def ph(key):
        planets = astro.get("planets", {})
        if not isinstance(planets, dict): return "not entered"
        entry = planets.get(key, {})
        return (entry.get("house") if isinstance(entry, dict) else None) or "not entered"
    def pr(key):
        planets = astro.get("planets", {})
        if not isinstance(planets, dict): return "no"
        entry = planets.get(key, {})
        return "YES" if isinstance(entry, dict) and entry.get("retrograde") else "no"

    return f"""{_SB_VOICE_RULES}

You are generating a Soul Blueprint Reading for {client.get('firstName','')} {client.get('lastName','')}.
This reading activates Rebirths. It does not give advice.
Draw ONLY from the calculated data provided below. Do not guess. Do not fill gaps with assumptions.
If data is missing for a section, name what is present and move forward.

{pre}

---
CALCULATED DATA FOR THIS READING:
---

CLIENT:
Name: {client.get('firstName','')} {client.get('middleName','') or ''} {client.get('lastName','')}
Date of Birth: {client.get('dateOfBirth','')}
Place of Birth: {client.get('placeOfBirth','') or 'not entered'}
Career Field: {client.get('careerField') or 'not entered'}
Career Expression: {client.get('careerExpression') or 'not entered'}

ASTROLOGY (Whole Sign):
Chart Ruler: {p('chartRuler')}
Rising: {p('rising')} | Rising Element: {p('risingElement')}
Sun: {p('sun')} | House: {ph('sun')} | Retrograde: {pr('sun')}
Moon: {p('moon')} | House: {ph('moon')} | Retrograde: {pr('moon')}
Mercury: {p('mercury')} | House: {ph('mercury')} | Retrograde: {pr('mercury')}
Venus: {p('venus')} | House: {ph('venus')} | Retrograde: {pr('venus')}
Mars: {p('mars')} | House: {ph('mars')} | Retrograde: {pr('mars')}
Jupiter: {p('jupiter')} | House: {ph('jupiter')} | Retrograde: {pr('jupiter')}
Saturn: {p('saturn')} | House: {ph('saturn')} | Retrograde: {pr('saturn')}
Uranus: {p('uranus')} | House: {ph('uranus')} | Retrograde: {pr('uranus')}
Neptune: {p('neptune')} | House: {ph('neptune')} | Retrograde: {pr('neptune')}
Pluto: {p('pluto')} | House: {ph('pluto')} | Retrograde: {pr('pluto')}
Chiron: {p('chiron')}
North Node: {p('northNode')} | House: {ph('northNode')} | Retrograde: ALWAYS
South Node: {p('southNode')} | House: {ph('southNode')} | Retrograde: ALWAYS
Midheaven: {p('midheaven')}
Black Moon Lilith: {p('blackMoonLilith')}
Part of Fortune: {p('partOfFortune')}
Major Aspects (with orbs): {astro.get('majorAspects') or 'not entered'}
Retrograde Planets: {', '.join(astro.get('retrogradeList', [])) or 'none'}
Dominant Element: {p('dominantElement')}
Dominant Modality: {p('dominantModality')}
Stelliums: {astro.get('stelliums') or 'none noted'}
Vedic Data: {astro.get('vedicData') or 'not entered'}

HUMAN DESIGN:
Type: {hd.get('type') or 'not entered'}
Strategy: {hd.get('strategy') or 'not entered'}
Authority: {hd.get('authority') or 'not entered'}
Profile: {hd.get('profile') or 'not entered'}
Definition: {hd.get('definition') or 'not entered'}
Incarnation Cross: {hd.get('incarnationCross') or 'not entered'}
Defined Centers: {json.dumps(hd.get('definedCenters',[]))}
Undefined Centers: {json.dumps(hd.get('undefinedCenters',[]))}
Defined Channels: {json.dumps(hd.get('channels',[]))}
Active Gates: {json.dumps(hd.get('activeGates',[]))}
Not Self Theme: {hd.get('notSelfTheme') or 'not entered'}
Signature Theme: {hd.get('signatureTheme') or 'not entered'}

PHOENIX REBIRTH NUMEROLOGY (calculated):
Full Name Number: {num.get('nameNumber',{}).get('raw')} (reduced: {num.get('nameNumber',{}).get('reduced')})
Life Path: {num.get('lifePath',{}).get('raw')} (reduced: {num.get('lifePath',{}).get('reduced')})
Birthday Number: {num.get('birthday',{}).get('raw')}
Soul Urge: {num.get('soulUrge',{}).get('raw')} (reduced: {num.get('soulUrge',{}).get('reduced')})
Personality: {num.get('personality',{}).get('raw')} (reduced: {num.get('personality',{}).get('reduced')})
Maturity Number: {num.get('maturity',{}).get('raw')} (reduced: {num.get('maturity',{}).get('reduced')})
Personal Year {current_year}: {num.get('personalYear',{}).get('raw')} (reduced: {num.get('personalYear',{}).get('reduced')})
Karmic Debts: {json.dumps(num.get('karmicDebts',[]))}

HEBREW METATRON CUBE (calculated - proprietary Phoenix Rebirth):
Convergence Power Points: {json.dumps(heb.get('convergencePoints',[]))}
Layer 1 Positions (Name - use "Hebrew Frequency of name letters" in reading prose): {json.dumps([str(pp.get('position'))+' '+str(pp.get('name','')) for pp in heb.get('layer1Positions',[])])}
Layer 2 Positions (Birth Date - use "Hebrew Frequency of birth date" in reading prose): {json.dumps([str(pp.get('position'))+' '+str(pp.get('name','')) for pp in heb.get('layer2Positions',[])])}
Position Statuses - AUTHORITATIVE SOURCE - DO NOT OVERRIDE: {json.dumps(heb.get('positionStatuses',{}))}
These statuses were determined by a separate AI evaluation of the Hebrew questionnaire responses before this prompt ran. They are final. Use them exactly. Never re-derive or override them.
Dominant Element: {heb.get('dominantElement')}
Elemental Wounds (zero activation): {json.dumps(heb.get('elementalWounds',[]))}
Fibonacci Activations: {json.dumps(heb.get('fibonacciActivations',[]))}

HEBREW POSITION PRE-COMPUTED FACTS - SOURCE OF TRUTH - DO NOT RE-DERIVE ANY OF THESE VALUES:
{json.dumps(heb_block)}
nameLetters = times fired through Hebrew Frequency of name letters. birthDate = times fired through Hebrew Frequency of birth date. fibonacci = fired through Fibonacci spiral (true/false). convergence = convergence power point (true/false). totalActivations = total count across all sources. felt = client's exact felt response word for word. status = authoritative AI-determined status. Use these values exactly. Do not recalculate or re-derive from any other data.

HEBREW POSITION-TO-LETTER MAP - LOCKED GEOMETRIC POSITIONS - DO NOT RE-DERIVE:
0=The Fool, 1=Aleph, 2=Bet, 3=Gimel, 4=Dalet, 5=Heh, 6=Vav, 7=Zayin, 8=Chet, 9=Tet, 10=Yod, 11=Kaf, 12=Lamed, 13=Mem, 14=Nun, 15=Samech, 16=Ayin, 17=Peh, 18=Tzadi, 19=Qof, 20=Resh, 21=Shin, 22=Tav

HEBREW POSITION DEFINITIONS - PROPRIETARY PHOENIX REBIRTH SYSTEM - USE ONLY THESE:
{json.dumps(_SB_HEB_POS_REF)}
These shadow expressions, healed expressions, and Rebirth notes are final and proprietary. Never substitute your own Hebrew knowledge for any definition in this table.

SELF-LOVE ASSESSMENT:
Self-Love Score: {ass.get('selfLoveScore')} / 85
Score Range: {ass.get('scoreRange')}
Attachment Style: {ass.get('attachmentStyle')}
S Count: {ass.get('sCount')} | A Count: {ass.get('aCount')} | D Count: {ass.get('dCount')} | F Count: {ass.get('fCount')}
Over-Giving Detected: {ass.get('overGiving')}
Bypass Detected: {ass.get('bypassDetected')}

HEBREW QUESTIONNAIRE RESPONSES (raw felt body responses - word for word):
{q_lines}

---
CRITICAL OUTPUT STRUCTURE - FOLLOW EXACTLY:
---

Your response begins with [JOURNEY_MAP] and nothing else comes before it.
No preamble. No introduction. No acknowledgment. The very first character of your response is the [ bracket.

STEP 1 - BUILD THE JOURNEY MAP:

Determine the path order using the Position Statuses object provided above. Those statuses are final and authoritative.

Rules:
- Position 21 (Shin): if status is anything other than not_activated, it is ALWAYS the first stop.
- If position 21 is not_activated, the first stop is the most significant healed convergence point.
- Position 0 (The Fool) is ALWAYS the final stop.
- Middle order: convergence power points first, then Fibonacci activations, then shadow positions (by activation count descending), then bridge positions (by activation count descending), then healed positions (by activation count descending).
- Include EVERY activated position (activation_count > 0 OR any not_activated position with a felt response in the Hebrew questionnaire).
- Minimum 4 positions. Maximum 10 positions.
- For not-activated positions with felt responses: frame as a frequency already carried naturally, a gift from past integration. Not about work to be done.
- Give each stop a label naming what this stop IS for this person specifically.

Output the journey map FIRST wrapped in these exact tags:
[JOURNEY_MAP]
{{"journey":[{{"position":21,"label":"Label for this stop"}},{{"position":9,"label":"Label for this stop"}},{{"position":0,"label":"Your Mission"}}]}}
[/JOURNEY_MAP]

STEP 2 - WRITE READING CONTENT FOR EVERY STOP:

For each position in the journey map, write the full reading content wrapped in position tags matching the position number exactly.

[POSITION_21]
Full reading prose for this position here...
[/POSITION_21]

[POSITION_9]
Stage narrative text here...
[/POSITION_9]

[POSITION_0]
Full closing mission prose here...
[/POSITION_0]

WHAT TO INCLUDE IN EACH POSITION BLOCK - woven into continuous prose, no section headers:

1. ACTIVATION SOURCE: Name which calculation fired this position and how many times. Use "Hebrew Frequency of your name letters" for Layer 1. "Hebrew Frequency of your birth date" for Layer 2. "Fibonacci spiral" for Fibonacci. "Convergence power point" when in both. Never use Layer 1 or Layer 2 as client-facing language.

2. FREQUENCY MEANING: What this Hebrew letter IS at its source. The archetype it carries. What it was always meant to activate.

3. FELT RESPONSE READING: What the client's body response reveals. The status for this position is already determined - use it exactly, do not re-derive from the felt response text. Quote their felt response if it is powerful.

4. CROSS-SYSTEM WEAVING: Specific astrology placements with house and sign. Specific Human Design centers, gates, or channels. Specific numerology progressions. Specific Self-Love assessment patterns. Always name the exact placement. Never be generic.

5. REBIRTH DIRECTION (shadow and bridge positions only): Woven into the close of that position's prose. A direction, not a list. A felt sense of walking forward. Never prescriptive.

NUMEROLOGY - CHAKRA LAYER ACTIVATION SYSTEM:
When any position block addresses numerology, use this system for every number:

Chakra Key (proprietary Phoenix Rebirth - locked):
0=Soul in Purest Form | 1=Root | 2=Sacral | 3=Solar Plexus | 4=Heart | 5=Throat | 6=Third Eye | 7=Crown | 8=Soul Star | 9=Earth Star | 11=Double Root | 22=Double Sacral | 33=Double Solar Plexus

Layer Activation Architecture:
Every multi-digit number is a layered chakra activation. First digit LEADS. Each subsequent digit INTEGRATES the one before it. The reduced single digit is the DESTINATION.
Single digit: direct chakra expression. Example: 9 = Earth Star frequency directly.
Double digit: double layer. Example: 23 = Sacral LEADS Solar Plexus.
Triple digit: triple layer. Example: 234 = Sacral LEADS Solar Plexus LEADS Heart. Arrives at Earth Star (9).

NEVER say "Your Name Number is X." NEVER say "234 reduces to 9."
ALWAYS name the leading chakra and what it drives. Then what each next chakra does as it integrates. Then arrive at the destination and name what the entire journey produces.
Apply this to EVERY number: Name Number, Life Path, Soul Urge, Personality, Birthday, Maturity, Personal Year {current_year}.
Master numbers (11, 22, 33) are NEVER reduced. Name the amplified demand and the amplified availability.

GATE INSTRUCTION - CHART-AGNOSTIC:
Identify the most significant defined gate or channel in THIS specific client's chart.
Weight gates connected to G-Center, Heart/Ego, or Throat as highest priority.
Name what it means for how this person operates and moves through the world. Do not soften this.
If Gate 51 is present in the active gates list: note it explicitly. Gate 51 is the gate of initiation through shock, the only gate connecting Heart/Ego directly to G-Center. It carries the frequency that enters a field like a bolt and cracks open what was sealed. Name what this means for this person, what it costs them, and what it makes possible. Do not soften this.
If Gate 51 is not present: do not mention it. Find what IS most significant for this chart.

CAREER FIELD ANALYSIS - weave into the position block that covers the Midheaven:
Career Field from intake: {client.get('careerField') or 'not entered'}
Career Expression from intake: {client.get('careerExpression') or 'not entered'}
Midheaven sign: pull from the Midheaven placement in the astrology data above.

Zodiac career rulership: {json.dumps(_SB_CAREER_RULERSHIP, indent=0)}
Midheaven expression modes: {json.dumps(_SB_CAREER_EXPR, indent=0)}

Layer 1 - Field Alignment: Is career_field in the list of fields ruled by their Midheaven sign?
Layer 2 (if aligned) - Expression Alignment: Is career_expression using the right energies?
Layer 3 - Timing: Cross-reference with current profection year lord and active transits to MC.
Weave all three into the reading prose as one continuous piece. If career_field is not entered, skip this analysis entirely.

HEBREW LANGUAGE RULES:
Never use "Layer 1" or "Layer 2" in any client-facing output.
Use "Hebrew Frequency of your name letters" for Layer 1. Use "Hebrew Frequency of your birth date" for Layer 2.

POSITION 0 - THE FOOL - ALWAYS THE FINAL STOP:
Synthesizes ALL systems. This is not a summary. It is the completion of the arc. The mission at soul level.
If position 22 (Tav) is activated, close with the Tav seal: the divine signature on everything this person came to complete.

STEP 3:
After the last [/POSITION_X] closing tag, output this on its own line and nothing after it:
[TIER2_CTA]
"""


def _sb_classify_statuses(questionnaire: list, l1_positions: list, l2_positions: list, fib_activations: list) -> dict:
    """Classify Hebrew position statuses from felt responses only.
    Matches buildHebrewInterpretPrompt + parseHebrewInterpretResult in SoulBlueprintAdmin.jsx exactly.
    not_activated = no felt response provided (regardless of numerological activation).
    Position 0 derived from dominant count across 1-22.
    """
    LETTER_MEANINGS = {
        1:  ("Aleph",  "The silent breath. The threshold. The void before sound."),
        2:  ("Bet",    "The sacred container. The house that holds what is created."),
        3:  ("Gimel",  "The camel. Bridge between worlds. Movement across wilderness."),
        4:  ("Dalet",  "The door. The threshold. The passage between what was and what is."),
        5:  ("Heh",    "The divine breath. The window of revelation. Presence."),
        6:  ("Vav",    "The nail. The connector between heaven and earth."),
        7:  ("Zayin",  "The sword of discernment. Divinity as protection."),
        8:  ("Chet",   "CHAI. Life itself. The sacred container where life grows."),
        9:  ("Tet",    "The serpent. The hidden goodness coiled and waiting to rise."),
        10: ("Yod",    "The divine spark. Smallest letter containing greatest power."),
        11: ("Kaf",    "The open palm. Power received and held."),
        12: ("Lamed",  "The teacher reaching toward heaven."),
        13: ("Mem",    "The primordial waters. The unconscious depths."),
        14: ("Nun",    "The fish. Faithful movement through the deep."),
        15: ("Samech", "The perfect circle. Divine support. Grace."),
        16: ("Ayin",   "The eye. The spring. Clear seeing beyond the physical."),
        17: ("Peh",    "The mouth. The voice. The breath of authentic expression."),
        18: ("Tzadi",  "The fish hook. The tzaddik. Pulling wisdom from the deep."),
        19: ("Qof",    "The horizon. The cycle that always returns."),
        20: ("Resh",   "The head. The beginning. The face turned toward what is next."),
        21: ("Shin",   "The divine fire. Love. The letter with which God signed creation."),
        22: ("Tav",    "The seal. The divine signature. The completion."),
    }

    # Only positions that have a felt response get classified by Claude
    q_with_responses = [r for r in questionnaire if (r.get("feltResponse") or "").strip()]

    statuses: dict = {}

    if q_with_responses:
        blocks = []
        for r in q_with_responses:
            pos = int(r.get("position", 0))
            name, meaning = LETTER_MEANINGS.get(pos, (r.get("letterName", ""), ""))
            block = f"Position {pos} — {name}: {meaning}\nFelt response: \"{r.get('feltResponse', '').strip()}\""
            notes = (r.get("notes") or "").strip()
            if notes:
                block += f"\nNotes: \"{notes}\""
            blocks.append(block)

        classify_prompt = (
            "You are a symbolic frequency classifier for the Hebrew Metatron's Cube system by Phoenix Rebirth.\n"
            "Your task is to classify written responses against their corresponding Hebrew letter archetypes. "
            "This is a symbolic resonance task only. Each response describes a person's felt connection to a sacred archetypal energy.\n"
            "Classification definitions:\n"
            "- \"healed\": Response resonates with the archetype's highest expression. Shows integration, flow, ease, or ownership of this energy.\n"
            "- \"shadow\": Response resonates with the archetype's contracted expression. Shows resistance, avoidance, or disconnection from this energy.\n"
            "- \"bridge\": Response resonates with both expressions simultaneously. Shows awareness of both the wound and the potential.\n"
            "- \"not_activated\": No response provided.\n"
            "Classify each position below:\n"
            "---\n"
            + "\n---\n".join(blocks)
            + "\n\nReturn ONLY a valid JSON object mapping position numbers as strings to status words.\n"
            "No explanation, no markdown, no extra text.\n"
            "Example: {\"1\": \"healed\", \"3\": \"shadow\", \"7\": \"bridge\"}"
        )

        try:
            raw = _call_claude(classify_prompt, max_tokens=512)
            ai_statuses = _parse_json_response(raw)
            for k, v in ai_statuses.items():
                statuses[str(k)] = v
        except Exception:
            pass

    # All positions 1-22 not returned by Claude default to not_activated
    for p in range(1, 23):
        if str(p) not in statuses:
            statuses[str(p)] = "not_activated"

    # Position 0 derived from dominant count across 1-22
    counts = {"healed": 0, "shadow": 0, "bridge": 0}
    for k, v in statuses.items():
        if k != "0" and v in counts:
            counts[v] += 1
    dominant = max(counts, key=counts.get) if any(counts.values()) else "bridge"
    statuses["0"] = dominant

    return statuses


def _run_soul_blueprint_generation(payload: dict, job_id: str) -> None:
    try:
        heb = payload.get("hebrew", {})
        q = payload.get("assessment", {}).get("hebrewQuestionnaire", [])

        # Step 1: classify position statuses via quick AI call
        statuses = _sb_classify_statuses(
            questionnaire=q,
            l1_positions=heb.get("layer1Positions", []),
            l2_positions=heb.get("layer2Positions", []),
            fib_activations=heb.get("fibonacciActivations", []),
        )
        payload["hebrew"]["positionStatuses"] = statuses

        # Step 2: build and send the full prompt to Claude
        prompt = _sb_build_prompt(payload)

        api_key = os.environ.get("CLAUDE_API_KEY", "")
        if not api_key:
            raise ValueError("Claude API key is not configured on the server. Add CLAUDE_API_KEY to Railway variables.")

        claude_body = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 8000,
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
        journey = journey_data.get("journey", [])

        positions_text: dict = {}
        for pm in re.finditer(r'\[POSITION_(\d+)\](.*?)\[/POSITION_\1\]', result_text, re.DOTALL):
            positions_text[int(pm.group(1))] = pm.group(2).strip()

        # Step 4: build CHART array for the HTML template
        l1 = heb.get("layer1Positions", [])
        l2 = heb.get("layer2Positions", [])
        fib_set = set(heb.get("fibonacciActivations", []))

        chart = []
        for stop in journey:
            pos = int(stop["position"])
            status = statuses.get(str(pos), "not_activated")
            l1c = sum(1 for p in l1 if int(p.get("position", -1)) == pos)
            l2c = sum(1 for p in l2 if int(p.get("position", -1)) == pos)
            fib_c = 1 if pos in fib_set else 0
            activation_count = max(l1c + l2c + fib_c, 1)

            felt = None
            if pos > 0:
                qi = next((r for r in q if int(r.get("position", 0)) == pos), None)
                if qi:
                    felt = qi.get("feltResponse", "").strip() or None

            chart.append({
                "position": pos,
                "status": status,
                "activation_count": activation_count,
                "reading": positions_text.get(pos, ""),
                "felt_response": felt,
                "rebirth_client": None,
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

        html = re.sub(
            r'// CLIENT_DATA_START\s*\nconst CLIENT = \{[^;]+\};',
            f'// CLIENT_DATA_START\nconst CLIENT = {client_json};',
            html,
        )
        html = re.sub(
            r'// CHART_DATA_START\s*\nconst CHART = \[\];',
            f'// CHART_DATA_START\nconst CHART = {chart_json};',
            html,
        )

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
                target=_run_claude_generation,
                args=(prompt, job_id),
                daemon=True,
            )
            t.start()
            self._send_json(200, {"job_id": job_id})

        elif path == "/sabian-symbols":
            try:
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
                        f"Phoenix Rebirth | {service_name} - {client_name}",
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

        elif path == "/classify-hebrew":
            questionnaire   = payload.get("questionnaire", [])
            l1_positions    = payload.get("layer1Positions", [])
            l2_positions    = payload.get("layer2Positions", [])
            fib_activations = payload.get("fibonacciActivations", [])
            try:
                statuses = _sb_classify_statuses(questionnaire, l1_positions, l2_positions, fib_activations)
                self._send_json(200, {"statuses": statuses})
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})

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
                "sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
                "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
                "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
                "pluto": swe.PLUTO, "chiron": swe.CHIRON, "northnode": swe.TRUE_NODE,
            }

            retrograde_map = {}
            for name, pid in planet_ids.items():
                result, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
                speed = result[3]
                retrograde_map[name] = speed < 0
            retrograde_map["southnode"] = retrograde_map.get("northnode", True)

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
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="Port for the local API server")
    parser.add_argument(
        "--ephe-path", required=False, default=None,
        help="Optional path to Swiss Ephemeris data files",
    )
    args = parser.parse_args()
    run_server(args.port, args.ephe_path)
