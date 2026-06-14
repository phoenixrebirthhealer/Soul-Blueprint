"""
transformation_pdf.py
Generates three types of Hidden Fears Template PDFs for the Phoenix Rebirth
6 Week Self-Love Transformation Program.
 
PDF Types:
  week1_baseline  - Week 1 responses with definitions
  week5_response  - Week 5 responses with definitions
  comparison      - Side by side comparison of Week 1 vs Week 5 with shifts highlighted
 
Called from Railway via POST /transformation-pdf
"""
 
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
 
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
GREEN      = colors.HexColor('#2e7d52')
GREEN_BG   = colors.HexColor('#e8f5ee')
 
 
def make_styles():
    return {
        'eyebrow': ParagraphStyle(
            'eyebrow', fontName='Helvetica', fontSize=7, textColor=MAGENTA,
            spaceAfter=4, spaceBefore=0, letterSpacing=3, alignment=TA_CENTER,
        ),
        'title': ParagraphStyle(
            'title', fontName='Helvetica-Bold', fontSize=22, textColor=PLUM_DEEP,
            spaceAfter=6, spaceBefore=0, alignment=TA_CENTER,
        ),
        'subtitle': ParagraphStyle(
            'subtitle', fontName='Helvetica', fontSize=11, textColor=GREY_MID,
            spaceAfter=4, alignment=TA_CENTER,
        ),
        'client_name': ParagraphStyle(
            'client_name', fontName='Helvetica-Bold', fontSize=13, textColor=PLUM,
            spaceAfter=2, alignment=TA_CENTER,
        ),
        'section_head': ParagraphStyle(
            'section_head', fontName='Helvetica-Bold', fontSize=8, textColor=GOLD,
            spaceBefore=16, spaceAfter=6, letterSpacing=2,
        ),
        'pair_word': ParagraphStyle(
            'pair_word', fontName='Helvetica-Bold', fontSize=10, textColor=PLUM_DEEP,
            spaceAfter=2,
        ),
        'pair_label': ParagraphStyle(
            'pair_label', fontName='Helvetica', fontSize=8, textColor=GREY_MID,
            spaceAfter=2,
        ),
        'definition': ParagraphStyle(
            'definition', fontName='Helvetica', fontSize=9, textColor=BLACK,
            spaceAfter=4, leading=14,
        ),
        'note_head': ParagraphStyle(
            'note_head', fontName='Helvetica-Bold', fontSize=8, textColor=MAGENTA,
            spaceBefore=12, spaceAfter=4, letterSpacing=1,
        ),
        'note_body': ParagraphStyle(
            'note_body', fontName='Helvetica', fontSize=10, textColor=BLACK,
            spaceAfter=6, leading=16,
        ),
        'stat': ParagraphStyle(
            'stat', fontName='Helvetica-Bold', fontSize=28, textColor=PLUM,
            alignment=TA_CENTER, spaceAfter=2,
        ),
        'stat_label': ParagraphStyle(
            'stat_label', fontName='Helvetica', fontSize=8, textColor=GREY_MID,
            alignment=TA_CENTER, letterSpacing=1,
        ),
        'footer': ParagraphStyle(
            'footer', fontName='Helvetica', fontSize=7, textColor=GREY_MID,
            alignment=TA_CENTER,
        ),
        'shift_label': ParagraphStyle(
            'shift_label', fontName='Helvetica-Bold', fontSize=8, textColor=GREEN,
            spaceAfter=2, letterSpacing=1,
        ),
        'body': ParagraphStyle(
            'body', fontName='Helvetica', fontSize=10, textColor=BLACK,
            spaceAfter=6, leading=16,
        ),
    }
 
 
HF_PAIRS = [
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
 
 
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.5)
    canvas.line(0.6 * inch, h - 0.45 * inch, w - 0.6 * inch, h - 0.45 * inch)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GREY_MID)
    canvas.drawCentredString(w / 2, 0.4 * inch, 'Phoenix Rebirth  |  Christina Stevens  |  Confidential')
    canvas.drawRightString(w - 0.6 * inch, 0.4 * inch, f'Page {doc.page}')
    canvas.restoreState()
 
 
def _normalize_definitions(raw_defs):
    """
    Normalize definitions regardless of whether PHP sent a JSON object or array.
    Returns dict keyed by int index, values are dicts of {word: definition_string}.
    """
    definitions = {}
    if isinstance(raw_defs, list):
        for i, v in enumerate(raw_defs):
            definitions[i] = v if isinstance(v, dict) else {}
    elif isinstance(raw_defs, dict):
        for k, v in raw_defs.items():
            try:
                idx = int(k)
            except (ValueError, TypeError):
                continue
            definitions[idx] = v if isinstance(v, dict) else {}
    return definitions
 
 
def _normalize_notes(raw_notes):
    """
    Normalize shared_notes regardless of whether PHP sent a JSON array or object.
    Returns a list of dicts.
    """
    if isinstance(raw_notes, list):
        return [n for n in raw_notes if isinstance(n, dict)]
    elif isinstance(raw_notes, dict):
        return [v for v in raw_notes.values() if isinstance(v, dict)]
    return []
 
 
def _normalize_answers(raw_answers):
    """
    Normalize answers. Returns dict with str keys.
    """
    if isinstance(raw_answers, dict):
        return {str(k): v for k, v in raw_answers.items()}
    elif isinstance(raw_answers, list):
        return {str(i): v for i, v in enumerate(raw_answers) if v is not None}
    return {}
 
 
def _get_def(definitions, pi, word):
    """Safely get definition for a word at pair index pi."""
    pair_defs = definitions.get(pi, definitions.get(str(pi), {}))
    if not isinstance(pair_defs, dict):
        return ''
    return pair_defs.get(word, '')
 
 
def build_single_response_pdf(client_name, round_label, date_completed,
                               answers, definitions, shared_notes):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.65*inch, rightMargin=0.65*inch,
        topMargin=0.75*inch, bottomMargin=0.65*inch,
    )
    S = make_styles()
    story = []
 
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph('PHOENIX REBIRTH', S['eyebrow']))
    story.append(Paragraph('Hidden Fears Template', S['title']))
    story.append(Paragraph(round_label, S['subtitle']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(client_name, S['client_name']))
    story.append(Paragraph(f'Completed {date_completed}', S['subtitle']))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GOLD, spaceAfter=16))
 
    if shared_notes:
        story.append(Paragraph('PRACTITIONER NOTES', S['section_head']))
        for note in shared_notes:
            if not isinstance(note, dict):
                continue
            story.append(Paragraph(f'Week {note.get("week", "")} Session', S['note_head']))
            story.append(Paragraph(note.get('notes', ''), S['note_body']))
        story.append(HRFlowable(width='100%', thickness=0.5, color=GREY_LIGHT, spaceAfter=12))
 
    story.append(Paragraph('YOUR RESPONSES', S['section_head']))
    story.append(Spacer(1, 4))
 
    for pi, pair in enumerate(HF_PAIRS):
        choice_idx = answers.get(str(pi))
        if choice_idx is None:
            continue
        try:
            choice_int = int(choice_idx)
        except (ValueError, TypeError):
            continue
        if choice_int not in (0, 1):
            continue
        chosen = pair[choice_int]
        other  = pair[1 - choice_int]
        definition = _get_def(definitions, pi, chosen)
 
        block = []
        block.append(Paragraph(
            f'<font color="#9e8fb0">{pi + 1}. {other} /</font> <b>{chosen}</b>',
            S['pair_word']
        ))
        if definition:
            block.append(Paragraph(definition, S['definition']))
        block.append(HRFlowable(
            width='100%', thickness=0.3,
            color=colors.HexColor('#e8e0f0'), spaceAfter=6
        ))
        story.append(KeepTogether(block))
 
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    buf.seek(0)
    return buf.read()
 
 
def build_comparison_pdf(client_name, date_w1, date_w5,
                         answers_w1, answers_w5,
                         definitions, shared_notes):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.65*inch, rightMargin=0.65*inch,
        topMargin=0.75*inch, bottomMargin=0.65*inch,
    )
    S = make_styles()
    story = []
 
    shifted_indexes = []
    for pi in range(len(HF_PAIRS)):
        a1 = answers_w1.get(str(pi))
        a5 = answers_w5.get(str(pi))
        if a1 is not None and a5 is not None:
            try:
                if int(a1) != int(a5):
                    shifted_indexes.append(pi)
            except (ValueError, TypeError):
                pass
    shift_count = len(shifted_indexes)
    pct = round((shift_count / len(HF_PAIRS)) * 100)
 
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph('PHOENIX REBIRTH', S['eyebrow']))
    story.append(Paragraph('Hidden Fears Template', S['title']))
    story.append(Paragraph('6 Week Transformation Comparison', S['subtitle']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(client_name, S['client_name']))
    story.append(Paragraph(f'Week 1: {date_w1}  |  Week 5: {date_w5}', S['subtitle']))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GOLD, spaceAfter=20))
 
    stat_data = [[
        Paragraph(str(shift_count), S['stat']),
        Paragraph(str(175 - shift_count), S['stat']),
        Paragraph(f'{pct}%', S['stat']),
    ],[
        Paragraph('PAIRS SHIFTED', S['stat_label']),
        Paragraph('PAIRS HELD', S['stat_label']),
        Paragraph('SHIFT RATE', S['stat_label']),
    ]]
    stat_table = Table(stat_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    stat_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEAFTER', (0,0), (1,1), 0.5, colors.HexColor('#e8e0f0')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(stat_table)
    story.append(HRFlowable(width='100%', thickness=0.5, color=GREY_LIGHT, spaceAfter=16))
 
    if shared_notes:
        story.append(Paragraph('PRACTITIONER NOTES', S['section_head']))
        for note in shared_notes:
            if not isinstance(note, dict):
                continue
            story.append(Paragraph(f'Week {note.get("week", "")} Session', S['note_head']))
            story.append(Paragraph(note.get('notes', ''), S['note_body']))
        story.append(HRFlowable(width='100%', thickness=0.5, color=GREY_LIGHT, spaceAfter=12))
 
    if shifted_indexes:
        story.append(Paragraph(f'WHAT MOVED  ({shift_count} pairs)', S['section_head']))
        story.append(Spacer(1, 4))
        for pi in shifted_indexes:
            pair = HF_PAIRS[pi]
            a1 = answers_w1.get(str(pi))
            a5 = answers_w5.get(str(pi))
            try:
                word1 = pair[int(a1)]
                word5 = pair[int(a5)]
            except (ValueError, TypeError, IndexError):
                continue
            def1 = _get_def(definitions, pi, word1)
            def5 = _get_def(definitions, pi, word5)
 
            block = []
            block.append(Paragraph(
                f'<font color="#9e8fb0">{pi + 1}. {pair[0]} / {pair[1]}</font>',
                S['pair_label']
            ))
            block.append(Paragraph(f'Week 1: <b>{word1}</b>', S['pair_word']))
            if def1:
                block.append(Paragraph(def1, S['definition']))
            block.append(Paragraph(
                '<font color="#2e7d52">&#8594; SHIFTED</font>',
                S['shift_label']
            ))
            block.append(Paragraph(f'Week 5: <b>{word5}</b>', S['pair_word']))
            if def5:
                block.append(Paragraph(def5, S['definition']))
            block.append(HRFlowable(
                width='100%', thickness=0.4,
                color=colors.HexColor('#c8f0d8'), spaceAfter=8
            ))
            story.append(KeepTogether(block))
 
    held = [pi for pi in range(len(HF_PAIRS)) if pi not in shifted_indexes]
    if held:
        story.append(PageBreak())
        story.append(Paragraph(f'WHAT HELD  ({len(held)} pairs)', S['section_head']))
        story.append(Spacer(1, 4))
        for pi in held:
            pair = HF_PAIRS[pi]
            a1 = answers_w1.get(str(pi))
            if a1 is None:
                continue
            try:
                chosen = pair[int(a1)]
            except (ValueError, TypeError, IndexError):
                continue
            definition = _get_def(definitions, pi, chosen)
 
            block = []
            block.append(Paragraph(
                f'<font color="#9e8fb0">{pi + 1}. {pair[0]} / {pair[1]}</font>  <b>{chosen}</b>',
                S['pair_word']
            ))
            if definition:
                block.append(Paragraph(definition, S['definition']))
            block.append(HRFlowable(
                width='100%', thickness=0.3,
                color=colors.HexColor('#e8e0f0'), spaceAfter=4
            ))
            story.append(KeepTogether(block))
 
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    buf.seek(0)
    return buf.read()
 
 
def generate_transformation_pdf(payload):
    """
    Main entry point called from Railway Flask route.
    Returns: bytes
    """
    pdf_type     = payload.get('pdf_type')
    client_name  = payload.get('client_name', 'Client')
    definitions  = _normalize_definitions(payload.get('definitions', {}))
    shared_notes = _normalize_notes(payload.get('shared_notes', []))
 
    if pdf_type == 'week1_baseline':
        answers = _normalize_answers(payload.get('answers_w1', {}))
        return build_single_response_pdf(
            client_name=client_name,
            round_label='Week 1 Baseline',
            date_completed=payload.get('date_completed', ''),
            answers=answers,
            definitions=definitions,
            shared_notes=[],
        )
    elif pdf_type == 'week5_response':
        answers = _normalize_answers(payload.get('answers_w5', {}))
        return build_single_response_pdf(
            client_name=client_name,
            round_label='Week 5 Response',
            date_completed=payload.get('date_completed', ''),
            answers=answers,
            definitions=definitions,
            shared_notes=[],
        )
    elif pdf_type == 'comparison':
        answers_w1 = _normalize_answers(payload.get('answers_w1', {}))
        answers_w5 = _normalize_answers(payload.get('answers_w5', {}))
        return build_comparison_pdf(
            client_name=client_name,
            date_w1=payload.get('date_w1', ''),
            date_w5=payload.get('date_w5', ''),
            answers_w1=answers_w1,
            answers_w5=answers_w5,
            definitions=definitions,
            shared_notes=shared_notes,
        )
    else:
        raise ValueError(f'Unknown pdf_type: {pdf_type}')
