"""
Awakening and Path Activation Transit Tracker
Phoenix Rebirth | soulReady

Approximation tool only. NOT a prediction system.
Every output carries the required disclaimer.
See TRANSIT_TRACKER_SPEC.md for full specification.

Requires: pip install pyswisseph
"""

import swisseph as swe
from datetime import datetime, date, timedelta
from flask import request, jsonify

DISCLAIMER = (
    "These are estimated activation windows based on planetary movement patterns. "
    "They are approximations, not predictions. Individual response to planetary transits "
    "varies significantly. This information is for self-awareness purposes only and is not "
    "a guarantee of any specific experience or timeline."
)

PLANET_IDS = {
    'sun':     swe.SUN,
    'moon':    swe.MOON,
    'mercury': swe.MERCURY,
    'venus':   swe.VENUS,
    'mars':    swe.MARS,
    'jupiter': swe.JUPITER,
    'saturn':  swe.SATURN,
    'uranus':  swe.URANUS,
    'neptune': swe.NEPTUNE,
    'pluto':   swe.PLUTO,
    'chiron':  swe.CHIRON,
    'north_node': swe.TRUE_NODE,
}

SIGN_RULERS = {
    'Aries':       ['mars'],
    'Taurus':      ['venus'],
    'Gemini':      ['mercury'],
    'Cancer':      ['moon'],
    'Leo':         ['sun'],
    'Virgo':       ['mercury'],
    'Libra':       ['venus'],
    'Scorpio':     ['mars', 'pluto'],
    'Sagittarius': ['jupiter'],
    'Capricorn':   ['saturn'],
    'Aquarius':    ['saturn', 'uranus'],
    'Pisces':      ['jupiter', 'neptune'],
}

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

RISING_SIGN_START = {
    'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90,
    'Leo': 120, 'Virgo': 150, 'Libra': 180, 'Scorpio': 210,
    'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330,
}


def date_to_jd(d):
    """Convert a date or datetime to Julian Day Number."""
    if isinstance(d, datetime):
        return swe.julday(d.year, d.month, d.day, d.hour + d.minute / 60.0)
    return swe.julday(d.year, d.month, d.day, 0.0)


def get_planet_longitude(planet_id, jd):
    """Return ecliptic longitude of a planet at Julian Day jd."""
    result, _ = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
    return result[0]


def longitude_to_sign_degree(longitude):
    """Return (sign_name, degree_within_sign) from ecliptic longitude."""
    sign_index = int(longitude // 30)
    degree = longitude % 30
    return SIGNS[sign_index], degree


def find_solar_return(birth_sun_longitude, birth_year, search_from_date):
    """
    Find the next solar return date on or after search_from_date.
    Binary search for the exact moment transiting Sun returns to natal Sun longitude.
    """
    start_jd = date_to_jd(search_from_date)
    end_jd = start_jd + 370

    def sun_diff(jd):
        lon = get_planet_longitude(swe.SUN, jd)
        diff = (lon - birth_sun_longitude + 360) % 360
        if diff > 180:
            diff -= 360
        return diff

    lo, hi = start_jd, end_jd
    for _ in range(50):
        mid = (lo + hi) / 2
        d = sun_diff(mid)
        if abs(d) < 0.001:
            break
        if d > 0:
            hi = mid
        else:
            lo = mid

    jd_result = (lo + hi) / 2
    year, month, day, _ = swe.revjul(jd_result)
    return date(int(year), int(month), int(day))


def get_profection_year(birth_date, rising_sign, as_of_date=None):
    """
    Calculate current profection year house, activated sign, and ruling planets.
    Formula: House = (age mod 12) + 1
    """
    if as_of_date is None:
        as_of_date = date.today()
    age = as_of_date.year - birth_date.year
    if (as_of_date.month, as_of_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    house_index = age % 12
    activated_house = house_index + 1

    rising_index = SIGNS.index(rising_sign)
    activated_sign_index = (rising_index + house_index) % 12
    activated_sign = SIGNS[activated_sign_index]
    activated_rulers = SIGN_RULERS.get(activated_sign, [])

    birth_sun_longitude = None
    try:
        birth_jd = date_to_jd(birth_date)
        birth_sun_longitude = get_planet_longitude(swe.SUN, birth_jd)
        solar_return = find_solar_return(birth_sun_longitude, birth_date.year, as_of_date)
        days_remaining = (solar_return - as_of_date).days
    except Exception:
        solar_return = None
        days_remaining = None

    return {
        'age': age,
        'activated_house': activated_house,
        'activated_sign': activated_sign,
        'activated_rulers': activated_rulers,
        'solar_return_date': solar_return.isoformat() if solar_return else None,
        'days_remaining_in_profection_year': days_remaining,
    }


def check_transit_window(transiting_longitude, natal_longitude, aspect_degrees=0, orb=5.0):
    """
    Check if a transiting planet is within orb of a natal point at a given aspect.
    Returns True if within orb.
    """
    target = (natal_longitude + aspect_degrees) % 360
    diff = abs((transiting_longitude - target + 180) % 360 - 180)
    return diff <= orb


def scan_transits_for_month(year, month, natal_points, profection_rulers):
    """
    Scan a single month for active transits.
    Returns list of triggered transit descriptions.
    """
    mid_day = date(year, month, 15)
    jd = date_to_jd(mid_day)
    triggered = []

    transit_checks = [
        ('Saturn crossing natal Ascendant', 'saturn', natal_points.get('ascendant'), 0),
        ('Saturn crossing natal Sun', 'saturn', natal_points.get('sun'), 0),
        ('Saturn crossing natal Moon', 'saturn', natal_points.get('moon'), 0),
        ('Saturn crossing natal Midheaven', 'saturn', natal_points.get('midheaven'), 0),
        ('Saturn crossing natal North Node', 'saturn', natal_points.get('north_node'), 0),
        ('Saturn Return', 'saturn', natal_points.get('saturn'), 0),
        ('Uranus opposition natal Uranus', 'uranus', natal_points.get('uranus'), 180),
        ('Uranus square natal Uranus', 'uranus', natal_points.get('uranus'), 90),
        ('Jupiter conjunct natal Neptune', 'jupiter', natal_points.get('neptune'), 0),
        ('Jupiter conjunct natal Chiron', 'jupiter', natal_points.get('chiron'), 0),
        ('Jupiter conjunct natal North Node', 'jupiter', natal_points.get('north_node'), 0),
        ('Pluto conjunct natal Sun', 'pluto', natal_points.get('sun'), 0),
        ('Pluto conjunct natal Moon', 'pluto', natal_points.get('moon'), 0),
        ('Pluto conjunct natal Ascendant', 'pluto', natal_points.get('ascendant'), 0),
        ('Pluto square natal Sun', 'pluto', natal_points.get('sun'), 90),
        ('Pluto square natal Moon', 'pluto', natal_points.get('moon'), 90),
        ('Nodal Return', 'north_node', natal_points.get('north_node'), 0),
    ]

    for label, planet_key, natal_lon, aspect in transit_checks:
        if natal_lon is None:
            continue
        planet_id = PLANET_IDS.get(planet_key)
        if planet_id is None:
            continue
        try:
            trans_lon = get_planet_longitude(planet_id, jd)
            if check_transit_window(trans_lon, natal_lon, aspect):
                triggered.append({
                    'transit': label,
                    'month': f"{year}-{month:02d}",
                })
        except Exception:
            continue

    for ruler in profection_rulers:
        natal_ruler_lon = natal_points.get(ruler)
        if natal_ruler_lon is None:
            continue
        planet_id = PLANET_IDS.get(ruler)
        if planet_id is None:
            continue
        try:
            trans_lon = get_planet_longitude(planet_id, jd)
            if check_transit_window(trans_lon, natal_ruler_lon, 0):
                triggered.append({
                    'transit': f"Profection year lord {ruler.capitalize()} conjunct natal {ruler.capitalize()}",
                    'month': f"{year}-{month:02d}",
                })
        except Exception:
            continue

    return triggered


def check_solar_return_proximity(birth_date, scan_date):
    """Check if scan_date falls within 7 days before the solar return."""
    birth_jd = date_to_jd(birth_date)
    birth_sun = get_planet_longitude(swe.SUN, birth_jd)
    sr_date = find_solar_return(birth_sun, birth_date.year, scan_date)
    days_until = (sr_date - scan_date).days
    return 0 <= days_until <= 7


def flag_level(count):
    if count >= 6:
        return "Major Activation Window"
    elif count >= 4:
        return "Active Window"
    elif count >= 3:
        return "Emerging Window"
    return None


def find_convergence_windows(all_monthly_transits):
    """
    Find months where 3+ transits cluster within a 6-month rolling window.
    Returns list of convergence window dicts.
    """
    month_keys = sorted(all_monthly_transits.keys())
    windows = []
    seen_starts = set()

    for i, start_month in enumerate(month_keys):
        window_months = [m for m in month_keys if m >= start_month][:6]
        transits_in_window = []
        for m in window_months:
            transits_in_window.extend(all_monthly_transits[m])

        unique_transit_names = list({t['transit'] for t in transits_in_window})
        count = len(unique_transit_names)
        level = flag_level(count)

        if level and start_month not in seen_starts:
            seen_starts.add(start_month)
            windows.append({
                'window_start': start_month,
                'window_end': window_months[-1],
                'flag_level': level,
                'transit_count': count,
                'transits': unique_transit_names,
            })

    return windows


def calculate_transit_map(birth_date, natal_points, rising_sign, as_of_date=None, months=36):
    """
    Main calculation function. Returns full transit map for the next N months.

    Args:
        birth_date: date object
        natal_points: dict of {point_name: ecliptic_longitude_float}
                      e.g. {'sun': 19.5, 'moon': 352.9, 'saturn': 270.4, ...}
        rising_sign: string e.g. 'Aquarius'
        as_of_date: date object, defaults to today
        months: number of months to scan (default 36)

    Returns:
        dict with profection_year, transit_windows, convergence_windows, disclaimer
    """
    if as_of_date is None:
        as_of_date = date.today()

    profection = get_profection_year(birth_date, rising_sign, as_of_date)
    profection_rulers = profection['activated_rulers']

    all_monthly = {}
    scan = as_of_date.replace(day=1)

    for _ in range(months):
        y, m = scan.year, scan.month
        month_key = f"{y}-{m:02d}"

        triggered = scan_transits_for_month(y, m, natal_points, profection_rulers)

        try:
            mid = date(y, m, 15)
            if check_solar_return_proximity(birth_date, mid):
                triggered.append({
                    'transit': 'Solar Return proximity (within 7 days)',
                    'month': month_key,
                })
        except Exception:
            pass

        if triggered:
            all_monthly[month_key] = triggered

        if m == 12:
            scan = date(y + 1, 1, 1)
        else:
            scan = date(y, m + 1, 1)

    transit_windows = []
    for month_key, transits in sorted(all_monthly.items()):
        for t in transits:
            transit_windows.append(t)

    convergence_windows = find_convergence_windows(all_monthly)

    return {
        'profection_year': profection,
        'transit_windows': transit_windows,
        'convergence_windows': convergence_windows,
        'disclaimer': DISCLAIMER,
        'scan_period_months': months,
        'scan_from': as_of_date.isoformat(),
    }


def parse_natal_points_from_api(astrology_data):
    """
    Parse natal chart longitudes from the Railway API astrology output format.
    Input format example: {'sun': 'Aries 18.95', 'moon': 'Pisces 2.92 House 2', ...}
    Returns dict of {point: ecliptic_longitude_float}
    """
    natal = {}
    sign_start = {
        'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90,
        'Leo': 120, 'Virgo': 150, 'Libra': 180, 'Scorpio': 210,
        'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330,
    }
    for point, val in astrology_data.items():
        if not isinstance(val, str):
            continue
        parts = val.strip().split()
        if len(parts) < 2:
            continue
        sign = parts[0]
        try:
            degree = float(parts[1].replace('°', '').replace(',', '.'))
            if sign in sign_start:
                natal[point.lower().replace(' ', '_')] = sign_start[sign] + degree
        except ValueError:
            continue
    return natal


def register_transit_tracker_route(app):
    @app.route('/transit-tracker', methods=['POST'])
    def transit_tracker():
        """
        POST body:
        {
          "birth_date": "1983-04-09",
          "rising_sign": "Aquarius",
          "astrology_data": {
            "sun": "Aries 18.95",
            "moon": "Pisces 2.92 House 2",
            "saturn": "Libra 3.20 House 9",
            ...
          },
          "months": 36
        }

        Returns full transit map with profection year, transit windows,
        convergence flags, and disclaimer.
        """
        data = request.get_json(force=True, silent=True) or {}

        birth_date_str = data.get('birth_date', '')
        rising_sign = data.get('rising_sign', '')
        astrology_data = data.get('astrology_data', {})
        months = int(data.get('months', 36))

        if not birth_date_str or not rising_sign:
            return jsonify({'error': 'birth_date and rising_sign are required'}), 400

        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'birth_date must be YYYY-MM-DD format'}), 400

        natal_points = parse_natal_points_from_api(astrology_data)
        if not natal_points:
            return jsonify({'error': 'Could not parse any natal points from astrology_data'}), 400

        result = calculate_transit_map(
            birth_date=birth_date,
            natal_points=natal_points,
            rising_sign=rising_sign,
            months=months,
        )
        return jsonify(result)
