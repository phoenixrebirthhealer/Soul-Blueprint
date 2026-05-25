"""
Hebrew Metatron's Cube — Felt Response Interpretation
Phoenix Rebirth | soulReady

Evaluates questionnaire felt responses against Hebrew letter position meanings using Claude.
Returns healed / shadow / bridge / not_activated per position.
Requires ANTHROPIC_API_KEY environment variable in Railway.
"""

import json
import os
import anthropic
from flask import request, jsonify

HEBREW_LETTER_DATA = {
    1:  {'name': 'Aleph',  'element': 'Air',   'meaning': 'The silent breath. The threshold. The void before sound.'},
    2:  {'name': 'Bet',    'element': 'Earth', 'meaning': 'The sacred container. The house that holds what is created.'},
    3:  {'name': 'Gimel',  'element': 'Fire',  'meaning': 'The camel. Bridge between worlds. Movement across wilderness.'},
    4:  {'name': 'Dalet',  'element': 'Earth', 'meaning': 'The door. The threshold. The passage between what was and what is.'},
    5:  {'name': 'Heh',    'element': 'Air',   'meaning': 'The divine breath. The window of revelation. Presence.'},
    6:  {'name': 'Vav',    'element': 'Earth', 'meaning': 'The nail. The connector between heaven and earth.'},
    7:  {'name': 'Zayin',  'element': 'Air',   'meaning': 'The sword of discernment. Divinity as protection.'},
    8:  {'name': 'Chet',   'element': 'Water', 'meaning': 'CHAI. Life itself. The sacred container where life grows.'},
    9:  {'name': 'Tet',    'element': 'Earth', 'meaning': 'The serpent. The hidden goodness coiled and waiting to rise.'},
    10: {'name': 'Yod',    'element': 'Fire',  'meaning': 'The divine spark. Smallest letter containing greatest power.'},
    11: {'name': 'Kaf',    'element': 'Fire',  'meaning': 'The open palm. Power received and held.'},
    12: {'name': 'Lamed',  'element': 'Air',   'meaning': 'The teacher reaching toward heaven.'},
    13: {'name': 'Mem',    'element': 'Water', 'meaning': 'The primordial waters. The unconscious depths.'},
    14: {'name': 'Nun',    'element': 'Water', 'meaning': 'The fish. Faithful movement through the deep.'},
    15: {'name': 'Samech', 'element': 'Fire',  'meaning': 'The perfect circle. Divine support. Grace.'},
    16: {'name': 'Ayin',   'element': 'Earth', 'meaning': 'The eye. The spring. Clear seeing beyond the physical.'},
    17: {'name': 'Peh',    'element': 'Air',   'meaning': 'The mouth. The voice. The breath of authentic expression.'},
    18: {'name': 'Tzadi',  'element': 'Water', 'meaning': 'The fish hook. The tzaddik. Pulling wisdom from the deep.'},
    19: {'name': 'Qof',    'element': 'Earth', 'meaning': 'The horizon. The cycle that always returns.'},
    20: {'name': 'Resh',   'element': 'Air',   'meaning': 'The head. The beginning. The face turned toward what is next.'},
    21: {'name': 'Shin',   'element': 'Fire',  'meaning': 'The divine fire. Love. The letter with which God signed creation.'},
    22: {'name': 'Tav',    'element': 'Earth', 'meaning': 'The seal. The divine signature. The completion.'},
}


def build_batch_prompt(questionnaire_items):
    """Build a single batch prompt for all questionnaire responses that have content."""
    blocks = []
    for item in questionnaire_items:
        pos = item.get('position')
        felt = (item.get('feltResponse') or '').strip()
        notes = (item.get('notes') or '').strip()
        if not felt:
            continue
        letter = HEBREW_LETTER_DATA.get(pos, {})
        name = letter.get('name', f'Position {pos}')
        element = letter.get('element', '')
        meaning = letter.get('meaning', '')
        block = f"Position {pos} — {name} ({element}): {meaning}\nFelt response: \"{felt}\""
        if notes:
            block += f"\nNotes: \"{notes}\""
        blocks.append(block)

    if not blocks:
        return None

    return (
        "You are evaluating spiritual self-assessment responses for the Hebrew Metatron's Cube Frequency System, "
        "a proprietary system created by Christina Stevens of Phoenix Rebirth.\n\n"
        "Each Hebrew letter position carries a sacred energy. You are evaluating how a person's felt experience "
        "aligns with that letter's energy field.\n\n"
        "Status definitions:\n"
        "- \"healed\": The person is fully embodying this letter's highest expression. Their response shows "
        "integration, flow, ease, or conscious ownership of this energy.\n"
        "- \"shadow\": The person is in the contracted, wounded, or unprocessed expression. Their response shows "
        "resistance, pain, avoidance, fear, or disconnection from this energy.\n"
        "- \"bridge\": The person is in active transition. Their response shows awareness of both the wound and "
        "the potential, or conscious movement between states.\n\n"
        "Evaluate each position below:\n\n"
        "---\n"
        + "\n---\n".join(blocks)
        + "\n\n"
        "Return ONLY a valid JSON object mapping position numbers (as strings) to status words.\n"
        "Include only positions that have responses. No explanation, no markdown, no extra text.\n"
        "Example: {\"1\": \"healed\", \"3\": \"shadow\", \"7\": \"bridge\"}"
    )


def call_claude_for_interpretation(questionnaire_items):
    """Send batch prompt to Claude and parse the response."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError('ANTHROPIC_API_KEY environment variable is not set in Railway')

    prompt = build_batch_prompt(questionnaire_items)
    if not prompt:
        return {}

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model='claude-opus-4-7',
        max_tokens=512,
        messages=[{'role': 'user', 'content': prompt}],
    )

    raw = message.content[0].text.strip()
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)
    return {int(k): v for k, v in parsed.items()}


def derive_position_zero(position_statuses):
    """Derive The Fool's status from the majority pattern of positions 1-22."""
    counts = {'healed': 0, 'shadow': 0, 'bridge': 0}
    for pos, status in position_statuses.items():
        if pos != 0 and status in counts:
            counts[status] += 1
    if not any(counts.values()):
        return 'bridge'
    return max(counts, key=counts.get)


def build_full_status_map(questionnaire, ai_statuses):
    """
    Build the complete positionStatuses dict for positions 0-22.
    Positions with no felt response = not_activated.
    Position 0 = derived from majority.
    """
    status_map = {}
    for pos in range(1, 23):
        item = next((q for q in questionnaire if q.get('position') == pos), None)
        felt = (item.get('feltResponse') or '').strip() if item else ''
        if not felt:
            status_map[pos] = 'not_activated'
        else:
            status_map[pos] = ai_statuses.get(pos, 'bridge')

    status_map[0] = derive_position_zero(status_map)
    return status_map


def register_hebrew_interpretation_route(app):
    @app.route('/hebrew-interpret', methods=['POST'])
    def hebrew_interpret():
        """
        POST body:
        {
          "questionnaire": [
            {"position": 1, "feltResponse": "...", "notes": "..."},
            {"position": 2, "feltResponse": "", "notes": ""},
            ...
          ]
        }

        Returns:
        {
          "positionStatuses": {
            "0": "healed",
            "1": "shadow",
            "2": "not_activated",
            ...
          }
        }
        """
        data = request.get_json(force=True, silent=True) or {}
        questionnaire = data.get('questionnaire', [])

        if not questionnaire:
            return jsonify({'error': 'questionnaire array is required'}), 400

        try:
            ai_statuses = call_claude_for_interpretation(questionnaire)
        except ValueError as e:
            return jsonify({'error': str(e)}), 500
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Claude returned unparseable response: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Interpretation failed: {str(e)}'}), 500

        full_status = build_full_status_map(questionnaire, ai_statuses)

        return jsonify({
            'positionStatuses': {str(k): v for k, v in full_status.items()}
        })
