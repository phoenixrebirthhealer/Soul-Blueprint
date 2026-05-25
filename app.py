import json
import os
from datetime import datetime
from pathlib import Path

import swisseph as swe
from flask import Flask, request, jsonify, make_response

from astrology_humandesign import (
    human_design_chart,
    human_design_chart_from_intake,
    set_ephemeris_path,
)
from survival_mode_pdf import register_survival_mode_pdf_route
from sabian_symbols import register_sabian_route
from transit_tracker import register_transit_tracker_route
from hebrew_interpretation import register_hebrew_interpretation_route

app = Flask(__name__)

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

@app.after_request
def add_cors(response):
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    resp = make_response('', 204)
    for k, v in CORS_HEADERS.items():
        resp.headers[k] = v
    return resp

ephe_path = os.environ.get('EPHE_PATH', None)
set_ephemeris_path(ephe_path)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/chart', methods=['POST'])
def chart():
    payload = request.get_json(force=True, silent=True) or {}

    date_str = payload.get('date')
    time_str = payload.get('time')
    if not date_str or not time_str:
        return jsonify({'error': "'date' and 'time' are required"}), 400

    try:
        year, month, day = [int(p) for p in date_str.split('-')]
        hour, minute = [int(p) for p in time_str.split(':')]
    except (ValueError, AttributeError):
        return jsonify({'error': 'Invalid date or time format'}), 400

    timezone_name = payload.get('timezone')
    timezone_offset = payload.get('timezoneOffset')
    location = payload.get('location')
    latitude = payload.get('latitude')
    longitude = payload.get('longitude')
    country_hint = payload.get('countryHint')

    tz_value = timezone_name if timezone_name is not None else (
        str(timezone_offset) if timezone_offset is not None else None
    )

    try:
        if latitude is not None and longitude is not None:
            result = human_design_chart(
                year, month, day, hour, minute,
                float(latitude), float(longitude),
                tz_value, 88,
            )
        elif location:
            result = human_design_chart_from_intake(
                year, month, day, hour, minute,
                location,
                timezone_offset=timezone_offset,
                timezone_name=timezone_name,
                country_hint=country_hint,
                design_offset_days=88,
            )
        else:
            return jsonify({'error': "Either 'location' or both 'latitude' and 'longitude' must be provided"}), 400

        result = _inject_retrograde(result, year, month, day, hour, minute, tz_value)
        return jsonify(result)

    except Exception as exc:
        return jsonify({'error': str(exc)}), 400


def _inject_retrograde(chart, year, month, day, hour, minute, tz_value):
    try:
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
            'sun': swe.SUN, 'moon': swe.MOON, 'mercury': swe.MERCURY,
            'venus': swe.VENUS, 'mars': swe.MARS, 'jupiter': swe.JUPITER,
            'saturn': swe.SATURN, 'uranus': swe.URANUS, 'neptune': swe.NEPTUNE,
            'pluto': swe.PLUTO, 'northnode': swe.MEAN_NODE, 'chiron': swe.CHIRON,
        }

        retrograde_map = {}
        for name, pid in planet_ids.items():
            res, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
            retrograde_map[name] = res[3] < 0

        if 'birth' in chart and 'planet_positions' in chart['birth']:
            for p in chart['birth']['planet_positions']:
                key = p['planet'].lower().replace(' ', '')
                if key in retrograde_map:
                    p['retrograde'] = retrograde_map[key]
    except Exception:
        pass

    return chart


register_survival_mode_pdf_route(app)
register_sabian_route(app)
register_transit_tracker_route(app)
register_hebrew_interpretation_route(app)


@app.route('/hebrew-cube-template', methods=['GET'])
def hebrew_cube_template():
    template_path = Path(__file__).parent / 'tcm-system' / 'hebrew_metatron_cube_template.html'
    content = template_path.read_text(encoding='utf-8')
    from flask import make_response
    resp = make_response(content)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
