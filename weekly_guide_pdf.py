"""
weekly_guide_pdf.py
Generates personalized weekly guide PDFs for the Phoenix Rebirth
6 Week Self-Love Transformation Program.

Weeks:
  1 - Root De-Armouring / Inner Child & Inner Teen
  2 - Boundaries, Self-Love & Self-Care Foundations
  3 - Emotional Release
  4 - Triggers, Breathwork & Grounding
  5 - Integration & Identity
  6 - Embodied Rebirth

Called from Railway via POST /weekly-guide-pdf
"""

import io
import os
import json
import urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# Brand colors
PLUM       = colors.HexColor('#2d1054')
PLUM_DEEP  = colors.HexColor('#0f0520')
GOLD       = colors.HexColor('#d4af37')
MAGENTA    = colors.HexColor('#c2185b')
CREAM      = colors.HexColor('#f5f0ff')
WHITE      = colors.white
BLACK      = colors.HexColor('#1a0a2e')
GREY_LIGHT = colors.HexColor('#e8e0f0')
GREY_MID   = colors.HexColor('#9e8fb0')
GREY_DARK  = colors.HexColor('#4a3060')

WEEK_TOPICS = {
    1: 'Root De-Armouring & Inner Child Work',
    2: 'Boundaries, Self-Love & Self-Care Foundations',
    3: 'Emotional Release',
    4: 'Triggers, Breathwork & Grounding',
    5: 'Integration & Identity',
    6: 'Embodied Rebirth',
}

# Hidden Fears words relevant to each week
WEEK_HF_WORDS = {
    1: ['Roots','Bone','Ancient','Inheritance','Fossil','Hollow','Foundation','Ancestor','Seed','Origin','Blood','Marrow','Echo','Myth','Memory'],
    2: ['Castle','Shield','Mask','Thorn','Cloak','Anchor','Veil','Wall','Boundary','Sovereign','Crown','Gate','Stone','Iron','Armor'],
    3: ['Ocean','Storm','Wave','Tide','Waterfall','Glacier','Volcano','Rain','River','Flood','Current','Descent','Tears','Mist','Fog'],
    4: ['Wound','Predator','Phantom','Shadow','Serpent','Venom','Scar','Trigger','Fracture','Rust','Decay','Tremor','Earthquake','Fault Line','Prey'],
    5: ['Spiral','Chrysalis','Emergence','Fusion','Becoming','Whole','Integration','Chrysalis','Crystal','Constellation','Myth','Labyrinth','Threshold'],
    6: ['Phoenix','Rebirth','Flame','Sovereign','Crown','Light','Home','Freedom','Flight','Bloom','Ember','Inferno','Awakening','Return','Destiny'],
}


def make_styles():
    return {
        'header_eyebrow': ParagraphStyle(
            'header_eyebrow',
            fontName='Helvetica',
            fontSize=7,
            textColor=GREY_MID,
            alignment=TA_CENTER,
            letterSpacing=2,
            spaceAfter=2,
        ),
        'header_brand': ParagraphStyle(
            'header_brand',
            fontName='Helvetica-Bold',
            fontSize=7,
            textColor=GOLD,
            alignment=TA_CENTER,
            letterSpacing=3,
            spaceAfter=0,
        ),
        'week_eyebrow': ParagraphStyle(
            'week_eyebrow',
            fontName='Helvetica',
            fontSize=8,
            textColor=MAGENTA,
            alignment=TA_CENTER,
            letterSpacing=3,
            spaceAfter=6,
        ),
        'week_title': ParagraphStyle(
            'week_title',
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=PLUM_DEEP,
            alignment=TA_CENTER,
            spaceAfter=4,
            leading=30,
        ),
        'week_subtitle': ParagraphStyle(
            'week_subtitle',
            fontName='Helvetica',
            fontSize=13,
            textColor=GREY_DARK,
            alignment=TA_CENTER,
            spaceAfter=8,
            leading=18,
        ),
        'personalized_note': ParagraphStyle(
            'personalized_note',
            fontName='Helvetica',
            fontSize=10,
            textColor=GREY_MID,
            alignment=TA_CENTER,
            spaceAfter=0,
            leading=15,
        ),
        'results_label': ParagraphStyle(
            'results_label',
            fontName='Helvetica',
            fontSize=8,
            textColor=GREY_MID,
            alignment=TA_CENTER,
            letterSpacing=2,
            spaceAfter=4,
        ),
        'score_big': ParagraphStyle(
            'score_big',
            fontName='Helvetica-Bold',
            fontSize=36,
            textColor=PLUM,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        'score_label': ParagraphStyle(
            'score_label',
            fontName='Helvetica',
            fontSize=10,
            textColor=GREY_MID,
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        'attachment_label': ParagraphStyle(
            'attachment_label',
            fontName='Helvetica',
            fontSize=8,
            textColor=GREY_MID,
            alignment=TA_CENTER,
            letterSpacing=2,
            spaceAfter=4,
        ),
        'attachment_value': ParagraphStyle(
            'attachment_value',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=PLUM,
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        'intro_text': ParagraphStyle(
            'intro_text',
            fontName='Helvetica',
            fontSize=10,
            textColor=BLACK,
            spaceAfter=6,
            leading=16,
            alignment=TA_JUSTIFY,
        ),
        'part_label': ParagraphStyle(
            'part_label',
            fontName='Helvetica-Bold',
            fontSize=7,
            textColor=MAGENTA,
            spaceBefore=20,
            spaceAfter=2,
            letterSpacing=3,
        ),
        'part_title': ParagraphStyle(
            'part_title',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=PLUM_DEEP,
            spaceAfter=12,
            leading=22,
        ),
        'section_head': ParagraphStyle(
            'section_head',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=PLUM,
            spaceBefore=14,
            spaceAfter=6,
            leading=16,
        ),
        'body': ParagraphStyle(
            'body',
            fontName='Helvetica',
            fontSize=10,
            textColor=BLACK,
            spaceAfter=8,
            leading=16,
            alignment=TA_JUSTIFY,
        ),
        'pull_quote': ParagraphStyle(
            'pull_quote',
            fontName='Helvetica-Oblique',
            fontSize=11,
            textColor=PLUM,
            spaceAfter=4,
            spaceBefore=4,
            leading=18,
            alignment=TA_CENTER,
            leftIndent=20,
            rightIndent=20,
        ),
        'homework_title': ParagraphStyle(
            'homework_title',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=GOLD,
            spaceBefore=10,
            spaceAfter=4,
            letterSpacing=1,
        ),
        'homework_label': ParagraphStyle(
            'homework_label',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=PLUM,
            spaceAfter=3,
        ),
        'homework_body': ParagraphStyle(
            'homework_body',
            fontName='Helvetica',
            fontSize=10,
            textColor=BLACK,
            spaceAfter=8,
            leading=16,
            leftIndent=12,
        ),
        'daily_item': ParagraphStyle(
            'daily_item',
            fontName='Helvetica',
            fontSize=10,
            textColor=BLACK,
            spaceAfter=5,
            leading=16,
            leftIndent=16,
        ),
        'closing': ParagraphStyle(
            'closing',
            fontName='Helvetica-Oblique',
            fontSize=11,
            textColor=PLUM,
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=4,
        ),
        'closing_name': ParagraphStyle(
            'closing_name',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=GREY_MID,
            alignment=TA_CENTER,
            spaceAfter=0,
            letterSpacing=1,
        ),
        'hf_note': ParagraphStyle(
            'hf_note',
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=MAGENTA,
            spaceAfter=6,
            leading=14,
        ),
    }


def header_footer(canvas, doc, client_name, week_num, week_topic):
    canvas.saveState()
    w, h = letter

    # Top bar
    canvas.setFillColor(PLUM_DEEP)
    canvas.rect(0, h - 0.5 * inch, w, 0.5 * inch, fill=1, stroke=0)

    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GREY_MID)
    canvas.drawString(0.6 * inch, h - 0.22 * inch, 'soulReady | 6 Week Self-Love Transformation Program')
    canvas.setFillColor(GREY_MID)
    canvas.drawRightString(w - 0.6 * inch, h - 0.22 * inch, f'Week {week_num} | {week_topic}')

    # Bottom bar
    canvas.setFillColor(GREY_LIGHT)
    canvas.rect(0, 0, w, 0.45 * inch, fill=1, stroke=0)

    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GREY_MID)
    canvas.drawString(0.6 * inch, 0.17 * inch, f'Phoenix Rebirth | Christina Stevens')
    canvas.drawRightString(w - 0.6 * inch, 0.17 * inch, f'Page {doc.page}')

    canvas.restoreState()


def build_cover_page(story, S, client_name, week_num, sl_score, sl_tier, attachment_style):
    """Build the cover page matching the example PDF layout."""
    story.append(Spacer(1, 0.3 * inch))

    # Brand header
    story.append(Paragraph('SOULREADY · PHOENIX REBIRTH · CHRISTINA STEVENS', S['header_brand']))
    story.append(Paragraph('6 Week Self-Love Transformation Program', S['header_eyebrow']))
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GOLD, spaceAfter=16))

    # Week label
    story.append(Paragraph(f'WEEK {week_num} PERSONALIZED GUIDE', S['week_eyebrow']))
    story.append(Spacer(1, 8))

    # Week title
    topic = WEEK_TOPICS.get(week_num, '')
    # Split long titles for visual balance
    story.append(Paragraph(topic, S['week_title']))
    story.append(Spacer(1, 16))

    # Personalized note
    story.append(Paragraph(
        'Personalized for your Self-Love Foundation and Attachment Style results.',
        S['personalized_note']
    ))
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width='60%', thickness=0.5, color=GREY_LIGHT, spaceAfter=20))

    # Results at a glance
    story.append(Paragraph('YOUR RESULTS AT A GLANCE', S['results_label']))
    story.append(Spacer(1, 10))

    # Score + attachment side by side
    score_data = [[
        Paragraph(f'{sl_score} / 85', S['score_big']),
        Paragraph('ATTACHMENT STYLE', S['attachment_label']),
    ],[
        Paragraph(' ', S['score_label']),
        Paragraph(' ', S['attachment_label']),
    ],[
        Paragraph(sl_tier, S['score_label']),
        Paragraph(attachment_style, S['attachment_value']),
    ]]
    score_table = Table(score_data, colWidths=[3.5 * inch, 3.5 * inch])
    score_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEAFTER', (0,0), (0,1), 0.5, GREY_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.25 * inch))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GOLD, spaceAfter=16))

    # Intro paragraph
    story.append(Paragraph(
        f'This guide is built from your scores. Everything in it speaks directly to your specific combination '
        f'and the specific work that combination requires in Week {week_num}.',
        S['intro_text']
    ))


def get_hf_relevant_words(week_num, hf_answers):
    """Extract Hidden Fears chosen words relevant to this week's theme."""
    if not hf_answers:
        return []
    relevant_keywords = WEEK_HF_WORDS.get(week_num, [])
    hf_pairs = [
        ['Fauna','Flora'],['Cleopatra','Nefertiti'],['Dog','Cat'],['Ocean','Mountain'],['Dawn','Dusk'],
        ['Fire','Ice'],['Gold','Silver'],['Sun','Moon'],['Forest','Desert'],['Rain','Snow'],
        ['Lion','Wolf'],['Rose','Lotus'],['Castle','Cottage'],['Thunder','Lightning'],['Eagle','Raven'],
        ['River','Lake'],['Sapphire','Emerald'],['Candle','Lantern'],['Silence','Music'],['Sword','Shield'],
        ['Dragon','Phoenix'],['Cave','Cliff'],['Tide','Current'],['Smoke','Mist'],['Honey','Salt'],
        ['Silk','Velvet'],['Crow','Dove'],['Copper','Bronze'],['Roots','Wings'],['Labyrinth','Spiral'],
        ['Ink','Blood'],['Anchor','Compass'],['Fossil','Seed'],['Veil','Mirror'],['Obsidian','Quartz'],
        ['Tide Pool','Open Sea'],['Ember','Ash'],['Cathedral','Temple'],['Whisper','Roar'],['Serpent','Butterfly'],
        ['Iron','Clay'],['Citrus','Berry'],['Fog','Storm'],['Map','Compass'],['Antler','Horn'],
        ['Lantern','Torch'],['Pearl','Diamond'],['Moss','Lichen'],['Clockwork','Organic'],['Abyss','Summit'],
        ['Feather','Stone'],['Tide','Wave'],['Amber','Jade'],['Hollow','Solid'],['Myth','Legend'],
        ['Bone','Flesh'],['Waterfall','Spring'],['Starlight','Moonlight'],['Cocoon','Chrysalis'],['Ritual','Ceremony'],
        ['Ancient','Eternal'],['Predator','Prey'],['Stillness','Motion'],['Wound','Scar'],['Hunger','Thirst'],
        ['Phantom','Shadow'],['Glacier','Volcano'],['Petal','Thorn'],['Marrow','Sinew'],['Tide','Season'],
        ['Crystal','Geode'],['Instinct','Intuition'],['Mask','Face'],['Archive','Oracle'],['Covenant','Contract'],
        ['Wilderness','Garden'],['Beacon','Signal'],['Rust','Decay'],['Gravity','Momentum'],['Pilgrim','Wanderer'],
        ['Ritual','Instinct'],['Fault Line','Horizon'],['Constellation','Galaxy'],['Threshold','Boundary'],['Sovereign','Servant'],
        ['Artifact','Relic'],['Tremor','Earthquake'],['Bloom','Wither'],['Venom','Antidote'],['Tide Table','Star Chart'],
        ['Crypt','Sanctuary'],['Wilderness','Wasteland'],['Fracture','Fusion'],['Descent','Ascent'],['Hunger','Longing'],
        ['Siren','Muse'],['Cloak','Crown'],['Vigil','Dream'],['Offering','Sacrifice'],['Exile','Return'],
        ['Vessel','Void'],['Mariner','Cartographer'],['Alchemy','Sorcery'],['Ruin','Foundation'],['Ember','Spark'],
        ['Threshold','Abyss'],['Witness','Participant'],['Covenant','Curse'],['Harvest','Famine'],['Inheritance','Legacy'],
        ['Cipher','Symbol'],['Wanderer','Settler'],['Tide','Undertow'],['Bloom','Seed'],['Phantom','Echo'],
        ['Gravity','Levity'],['Feral','Tamed'],['Oracle','Prophet'],['Current','Stillwater'],['Sovereign','Exile'],
        ['Hunger','Satiation'],['Wound','Gift'],['Labyrinth','Crossroads'],['Veil','Revelation'],['Descent','Initiation'],
        ['Relic','Blueprint'],['Storm','Calm'],['Predator','Guardian'],['Fossil','Blueprint'],['Hollow','Sacred'],
        ['Fracture','Healing'],['Myth','Memory'],['Beacon','Anchor'],['Chrysalis','Emergence'],['Tidal','Lunar'],
        ['Covenant','Freedom'],['Archive','Flame'],['Threshold','Return'],['Wilderness','Temple'],['Descent','Surrender'],
        ['Echo','Origin'],['Feral','Sovereign'],['Hunger','Purpose'],['Wound','Wisdom'],['Phantom','Presence'],
        ['Ruin','Rebirth'],['Current','Destiny'],['Veil','Truth'],['Labyrinth','Liberation'],['Shadow','Light'],
        ['Ember','Inferno'],['Anchor','Flight'],['Fossil','Future'],['Hollow','Whole'],['Myth','Awakening'],
        ['Bone','Spirit'],['Tide','Transformation'],['Silence','Thunder'],['Cocoon','Freedom'],['Ritual','Revolution'],
        ['Ancient','Emerging'],['Predator','Creator'],['Stillness','Becoming'],['Wound','Warrior'],['Hunger','Vision'],
        ['Phantom','Truth'],['Glacier','Current'],['Petal','Flame'],['Marrow','Soul'],['Crystal','Chaos'],
        ['Instinct','Destiny'],['Mask','Truth'],['Archive','Prophecy'],['Covenant','Becoming'],['Wilderness','Home'],
    ]

    matched = []
    for pi, pair in enumerate(hf_pairs):
        choice = hf_answers.get(str(pi), hf_answers.get(pi, None))
        if choice is None:
            continue
        try:
            chosen_word = pair[int(choice)]
        except (ValueError, TypeError, IndexError):
            continue
        if chosen_word in relevant_keywords:
            matched.append(chosen_word)

    return matched


def call_claude(prompt, api_key, max_tokens=4000):
    """Call Claude API and return the text response."""
    body = json.dumps({
        'model': 'claude-sonnet-4-6',
        'max_tokens': max_tokens,
        'messages': [{'role': 'user', 'content': prompt}],
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=body,
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    return data['content'][0]['text'].strip()


def generate_weekly_guide_content(week_num, client_name, sl_score, sl_tier,
                                   attachment_style, hf_words, api_key):
    """
    Call Claude to generate the personalized guide content.
    Returns a dict with keys: part1, part2, part3, homework_reflection,
    homework_daily, closing_line, pull_quotes (list of 2-3)
    """
    topic = WEEK_TOPICS.get(week_num, '')
    hf_context = ''
    if hf_words:
        hf_context = f'\n\nHIDDEN FEARS RELEVANT WORDS (chosen by this client, weave in naturally where they apply):\n{", ".join(hf_words)}'

    voice_rules = """
VOICE (NON-NEGOTIABLE):
- Write in the voice of Christina Stevens. Direct, warm, fierce, unfiltered, deeply personal.
- Never use em dashes anywhere. Ever. Not once.
- Never use the word medicine. Use Rebirth instead.
- Never use disorder, condition, or diagnosis. Use wiring pattern or nervous system design.
- Write directly to the client as "you". Never "clients like you" or "people with your profile".
- Be specific. Not warm and general. Specific to THIS score and THIS attachment style.
- Short sentences land harder than long ones. Use them.
- Pull quotes should feel like they were written for this specific person, not a motivational poster.
- The tone is: I see you. I know what this costs. Here is the specific work.
- Never soften the truth. Deliver it with care but deliver it fully.
- Homework assignments are specific and actionable. Not vague invitations.
""".strip()

    prompt = f"""{voice_rules}

You are generating a Week {week_num} Personalized Guide for the Phoenix Rebirth 6 Week Self-Love Transformation Program.

CLIENT: {client_name}
SELF-LOVE SCORE: {sl_score} / 85
SELF-LOVE TIER: {sl_tier}
ATTACHMENT STYLE: {attachment_style}
WEEK TOPIC: {topic}{hf_context}

Generate the complete guide content. Return ONLY a valid JSON object with these exact keys, no preamble, no markdown:

{{
  "score_opening": "2-3 paragraphs. What their specific score actually means for this week's topic. Direct. Personal. No fluff.",
  "attachment_explanation": "2-3 paragraphs. What their specific attachment style means in the context of this week's topic. Name the specific patterns that show up.",
  "pull_quote_1": "One sentence. The most piercing truth about their score + attachment combo. No em dashes.",
  "part2_title": "Short title for Part 2 (the main topic section)",
  "part2_content": "3-4 paragraphs. The specific work for this week's topic calibrated to their exact attachment style. Include at least one subheading within the content using the format [SUBHEAD: Title Here] on its own line.",
  "pull_quote_2": "One sentence. A truth about the specific work in Part 2. No em dashes.",
  "part3_title": "Short title for Part 3 (the skill or practice section)",
  "part3_content": "2-3 paragraphs. The specific skill or capacity this profile is missing and how to begin developing it. Direct. Specific.",
  "pull_quote_3": "One sentence. A truth about the skill in Part 3. No em dashes.",
  "homework_reflection": [
    {{"title": "Reflection prompt title", "body": "The full prompt. Specific. Not generic."}},
    {{"title": "Reflection prompt title", "body": "The full prompt. Specific. Not generic."}},
    {{"title": "Reflection prompt title", "body": "The full prompt. Specific. Not generic."}}
  ],
  "homework_daily": [
    "Daily practice 1. One sentence. Specific and actionable.",
    "Daily practice 2. One sentence. Specific and actionable.",
    "Daily practice 3. One sentence. Specific and actionable."
  ],
  "homework_closing": "One sentence directing them to bring specific work to the next session.",
  "closing_line": "The final line of the guide. Beautiful. Personal. In Christina's voice."
}}"""

    text = call_claude(prompt, api_key, max_tokens=4000)
    # Strip markdown fences if present
    import re
    text = re.sub(r'^```\w*\n?', '', text).rstrip('`').strip()
    return json.loads(text)


def build_guide_pdf(payload):
    """
    Main entry point. Returns PDF bytes.

    payload keys:
      week_number: int
      client_name: str
      sl_score: int
      sl_tier: str
      attachment_style: str
      hf_answers: dict (optional, from hidden fears week 1)
    """
    api_key = os.environ.get('CLAUDE_API_KEY', '')
    if not api_key:
        raise ValueError('CLAUDE_API_KEY not set')

    week_num       = int(payload.get('week_number', 2))
    client_name    = payload.get('client_name', 'Client')
    sl_score       = int(payload.get('sl_score', 0))
    sl_tier        = payload.get('sl_tier', '')
    attachment     = payload.get('attachment_style', '')
    hf_answers     = payload.get('hf_answers', {})

    # Normalize hf_answers keys
    if isinstance(hf_answers, list):
        hf_answers = {str(i): v for i, v in enumerate(hf_answers) if v is not None}
    elif isinstance(hf_answers, dict):
        hf_answers = {str(k): v for k, v in hf_answers.items()}
    else:
        hf_answers = {}

    # Get relevant Hidden Fears words for this week
    hf_words = get_hf_relevant_words(week_num, hf_answers)

    # Generate content via Claude
    content = generate_weekly_guide_content(
        week_num, client_name, sl_score, sl_tier,
        attachment, hf_words, api_key
    )

    # Build PDF
    buf = io.BytesIO()
    topic = WEEK_TOPICS.get(week_num, '')

    def _hf(canvas, doc):
        header_footer(canvas, doc, client_name, week_num, topic)

    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.65 * inch,
    )
    S = make_styles()
    story = []

    # COVER PAGE
    build_cover_page(story, S, client_name, week_num, sl_score, sl_tier, attachment)

    # PART ONE - What Your Scores Are Telling You
    story.append(PageBreak())
    story.append(Paragraph('PART ONE', S['part_label']))
    story.append(Paragraph('What Your Scores Are Telling You', S['part_title']))
    story.append(HRFlowable(width='100%', thickness=0.3, color=GREY_LIGHT, spaceAfter=12))

    for para in content.get('score_opening', '').split('\n\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), S['body']))

    # Pull quote 1
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width='40%', thickness=0.3, color=GOLD, spaceAfter=8))
    story.append(Paragraph(f'"{content.get("pull_quote_1", "")}"', S['pull_quote']))
    story.append(HRFlowable(width='40%', thickness=0.3, color=GOLD, spaceAfter=12))
    story.append(Spacer(1, 4))

    for para in content.get('attachment_explanation', '').split('\n\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), S['body']))

    # Hidden Fears note if applicable
    if hf_words:
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f'Your Hidden Fears responses this week surface words like {", ".join(hf_words[:4])}. '
            f'These are not random. They are the language your subconscious is already using for this work.',
            S['hf_note']
        ))

    # PART TWO
    story.append(PageBreak())
    story.append(Paragraph('PART TWO', S['part_label']))
    story.append(Paragraph(content.get('part2_title', ''), S['part_title']))
    story.append(HRFlowable(width='100%', thickness=0.3, color=GREY_LIGHT, spaceAfter=12))

    part2_raw = content.get('part2_content', '')
    for para in part2_raw.split('\n\n'):
        para = para.strip()
        if not para:
            continue
        if para.startswith('[SUBHEAD:') and para.endswith(']'):
            subhead = para[9:-1].strip()
            story.append(Paragraph(subhead, S['section_head']))
        else:
            story.append(Paragraph(para, S['body']))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width='40%', thickness=0.3, color=GOLD, spaceAfter=8))
    story.append(Paragraph(f'"{content.get("pull_quote_2", "")}"', S['pull_quote']))
    story.append(HRFlowable(width='40%', thickness=0.3, color=GOLD, spaceAfter=12))

    # PART THREE
    story.append(PageBreak())
    story.append(Paragraph('PART THREE', S['part_label']))
    story.append(Paragraph(content.get('part3_title', ''), S['part_title']))
    story.append(HRFlowable(width='100%', thickness=0.3, color=GREY_LIGHT, spaceAfter=12))

    for para in content.get('part3_content', '').split('\n\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), S['body']))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width='40%', thickness=0.3, color=GOLD, spaceAfter=8))
    story.append(Paragraph(f'"{content.get("pull_quote_3", "")}"', S['pull_quote']))
    story.append(HRFlowable(width='40%', thickness=0.3, color=GOLD, spaceAfter=12))

    # HOMEWORK PAGE
    story.append(PageBreak())
    story.append(Paragraph(f'WEEK {week_num} HOMEWORK', S['week_eyebrow']))
    story.append(Paragraph('Your Personalized Assignments', S['part_title']))
    story.append(HRFlowable(width='100%', thickness=0.3, color=GREY_LIGHT, spaceAfter=8))
    story.append(Paragraph(
        'These assignments are built specifically from your score and your attachment profile. They are not generic. Do not skim them.',
        S['body']
    ))
    story.append(Spacer(1, 8))

    # Reflection
    story.append(Paragraph('REFLECTION WORK', S['homework_title']))
    for item in content.get('homework_reflection', []):
        story.append(Paragraph(item.get('title', ''), S['homework_label']))
        story.append(Paragraph(item.get('body', ''), S['homework_body']))

    # Daily
    story.append(Spacer(1, 6))
    story.append(Paragraph('DAILY PRACTICE', S['homework_title']))
    for item in content.get('homework_daily', []):
        story.append(Paragraph(f'- {item}', S['daily_item']))

    story.append(Spacer(1, 12))
    story.append(Paragraph(content.get('homework_closing', ''), S['body']))

    # Closing
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GOLD, spaceAfter=16))
    story.append(Paragraph('Heal from the Root. Bloom in your Truth.', S['closing']))
    story.append(Paragraph('Christina Stevens | Phoenix Rebirth', S['closing_name']))

    doc.build(story, onFirstPage=_hf, onLaterPages=_hf)
    buf.seek(0)
    return buf.read()
