import json
import math
import os
import shutil
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import swisseph as swe

SWISS_EPHEMERIS_GITHUB_RAW = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/"
LOCAL_EPHE_PATH = os.path.join(os.path.dirname(__file__), "ephe")
REQUIRED_EPHEMERIS_FILES = [
    "seas_18.se1",
    "sepl_18.se1",
    "semo_18.se1",
    "seasnam.txt",
    "swe_deltat.inactive.txt",
]

PLANET_NAMES = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS),
    ("Mars", swe.MARS),
    ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN),
    ("Uranus", swe.URANUS),
    ("Neptune", swe.NEPTUNE),
    ("Pluto", swe.PLUTO),
    ("North Node", swe.TRUE_NODE),
]

SIGN_NAMES = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

# Human Design gate order around the zodiac wheel, hardcoded from the HD wheel sequence.
# This sequence is offset from 0° Aries so the first segment begins at 28°15' Pisces / 0° Aries = Gate 25.
# The offset has been tuned to match verified HD gate boundary behavior for the 61/62 channel.
GATE_NUMBERS_BY_INDEX = [
    25, 17, 21, 51, 42, 3, 27, 24, 2, 23, 8, 20,
    16, 35, 45, 12, 15, 52, 39, 53, 62, 56, 31, 33,
    7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57,
    32, 50, 28, 44, 1, 43, 14, 34, 9, 5, 26, 11,
    10, 58, 38, 54, 61, 60, 41, 19, 13, 49, 30, 55,
    37, 63, 22, 36,
]
HD_GATE_WIDTH_DEGREES = 360.0 / 64.0
HD_GATE_OFFSET_DEGREES = 1.97

SPECIAL_PLANETARY_POINTS = [
    ("Chiron", swe.CHIRON),
    ("Black Moon Lilith", swe.MEAN_APOG),
]

CENTER_GATE_MAP = {
    "Head": {64, 61, 63},
    "Ajna": {4, 17, 11, 24, 43, 47},
    "Throat": {12, 16, 20, 23, 31, 33, 35, 45, 56, 62},
    "G-Center": {1, 2, 7, 10, 13, 15, 25, 46},
    "Heart/Ego": {21, 26, 40, 51},
    "Solar Plexus": {6, 22, 30, 36, 37, 49, 55},
    "Sacral": {3, 5, 9, 14, 27, 29, 34, 59},
    "Spleen": {18, 28, 32, 44, 48, 50, 57},
    "Root": {39, 52, 53, 54, 58, 60, 38, 41},
}

CHANNEL_DEFINITIONS = [
    {"name": "The Channel of Inspiration", "gates": (1, 8), "centers": ("G-Center", "Throat")},
    {"name": "The Channel of the Beat", "gates": (2, 14), "centers": ("G-Center", "Sacral")},
    {"name": "The Channel of Mutation", "gates": (3, 60), "centers": ("Root", "Sacral")},
    {"name": "The Channel of Logic", "gates": (4, 63), "centers": ("Ajna", "Head")},
    {"name": "The Channel of Rhythm", "gates": (5, 15), "centers": ("Sacral", "G-Center")},
    {"name": "The Channel of Intimacy", "gates": (6, 59), "centers": ("Throat", "Sacral")},
    {"name": "The Channel of the Alpha", "gates": (7, 31), "centers": ("G-Center", "Throat")},
    {"name": "The Channel of Struggle", "gates": (9, 52), "centers": ("Sacral", "Root")},
    {"name": "The Channel of Awakening", "gates": (10, 20), "centers": ("G-Center", "Throat")},
    {"name": "The Channel of Curiosity", "gates": (11, 56), "centers": ("Ajna", "Throat")},
    {"name": "The Channel of Openness", "gates": (12, 22), "centers": ("Throat", "G-Center")},
    {"name": "The Channel of the Prodigal", "gates": (13, 33), "centers": ("G-Center", "Throat")},
    {"name": "The Channel of Power", "gates": (16, 48), "centers": ("Throat", "Spleen")},
    {"name": "The Channel of Judgment", "gates": (18, 58), "centers": ("Spleen", "Root")},
    {"name": "The Channel of Synthesis", "gates": (19, 49), "centers": ("G-Center", "Solar Plexus")},
    {"name": "The Channel of Charisma", "gates": (20, 34), "centers": ("Throat", "Sacral")},
    {"name": "The Channel of Community", "gates": (21, 45), "centers": ("Heart/Ego", "Throat")},
    {"name": "The Channel of Structuring", "gates": (23, 43), "centers": ("Throat", "Ajna")},
    {"name": "The Channel of the Brainwave", "gates": (24, 61), "centers": ("Ajna", "Head")},
    {"name": "The Channel of Initiation", "gates": (25, 51), "centers": ("G-Center", "Heart/Ego")},
    {"name": "The Channel of Surrender", "gates": (26, 44), "centers": ("Heart/Ego", "Throat")},
    {"name": "The Channel of Preservation", "gates": (27, 50), "centers": ("Sacral", "Spleen")},
    {"name": "The Channel of Struggle", "gates": (28, 38), "centers": ("Spleen", "Root")},
    {"name": "The Channel of Discovery", "gates": (29, 46), "centers": ("Sacral", "G-Center")},
    {"name": "The Channel of Recognition", "gates": (30, 41), "centers": ("Solar Plexus", "Root")},
    {"name": "The Channel of Transformation", "gates": (32, 54), "centers": ("Spleen", "Root")},
    {"name": "The Channel of Exploration", "gates": (34, 10), "centers": ("Sacral", "G-Center")},
    {"name": "The Channel of Power", "gates": (34, 57), "centers": ("Sacral", "Spleen")},
    {"name": "The Channel of Perfected Form", "gates": (57, 10), "centers": ("Spleen", "G-Center")},
    {"name": "The Channel of Transitoriness", "gates": (35, 36), "centers": ("Sacral", "Root")},
    {"name": "The Channel of Community", "gates": (37, 40), "centers": ("Heart/Ego", "Root")},
    {"name": "The Channel of Emoting", "gates": (39, 55), "centers": ("Root", "Solar Plexus")},
    {"name": "The Channel of Maturation", "gates": (42, 53), "centers": ("Root", "Spleen")},
    {"name": "The Channel of Synthesis", "gates": (49, 19), "centers": ("Solar Plexus", "G-Center")},
    {"name": "The Channel of Abstraction", "gates": (47, 64), "centers": ("Ajna", "Head")},
    {"name": "The Channel of Details", "gates": (62, 17), "centers": ("Throat", "Ajna")},
]

DEFINITION_LABELS = {
    1: "Single Definition",
    2: "Split Definition",
    3: "Triple Split Definition",
    4: "Quadruple Split Definition",
}

DIGESTION_LABELS = {
    1: "Open",
    2: "Light",
    3: "Heavy",
    4: "Slow",
    5: "Hot",
    6: "Cold",
}

ENVIRONMENT_LABELS = {
    1: "Kitchens",
    2: "Markets",
    3: "Workplaces",
    4: "Communities",
    5: "Schools",
    6: "Camps",
}

DESIGN_SENSE_LABELS = {
    1: "Taste",
    2: "Sight",
    3: "Hearing",
    4: "Feeling",
    5: "Touch",
    6: "Awareness",
}


def line_from_longitude(longitude: float) -> int:
    longitude = normalize_longitude(longitude)
    adjusted = normalize_longitude(longitude + HD_GATE_OFFSET_DEGREES)
    gate_position = adjusted / HD_GATE_WIDTH_DEGREES
    within_gate = gate_position - math.floor(gate_position)
    line = int(math.floor(within_gate * 6 + 1e-12)) + 1
    return min(max(line, 1), 6)


def _gates_to_centers(active_gates: set) -> Dict[str, bool]:
    centers = {center: False for center in CENTER_GATE_MAP}
    for channel in CHANNEL_DEFINITIONS:
        a, b = channel["gates"]
        if a in active_gates and b in active_gates:
            left, right = channel["centers"]
            centers[left] = True
            centers[right] = True
    return centers


def _active_channels(active_gates: set) -> List[Dict[str, object]]:
    active = []
    for channel in CHANNEL_DEFINITIONS:
        a, b = channel["gates"]
        if a in active_gates and b in active_gates:
            active.append(
                {
                    "name": channel["name"],
                    "gates": [a, b],
                    "centers": list(channel["centers"]),
                }
            )
    return active


def _definition_from_channels(defined_centers: Dict[str, bool], active_channels: List[Dict[str, object]]) -> Dict[str, object]:
    defined = [center for center, is_defined in defined_centers.items() if is_defined]
    if not defined:
        return {"type": "Reflector", "groups": 0}

    graph = {center: set() for center in defined}
    for channel in active_channels:
        left, right = channel["centers"]
        if left in graph and right in graph:
            graph[left].add(right)
            graph[right].add(left)
    visited = set()
    components = 0
    for center in defined:
        if center in visited:
            continue
        components += 1
        stack = [center]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(graph[current] - visited)
    label = DEFINITION_LABELS.get(components, f"{components}-Split Definition")
    return {"type": label, "groups": components}


def _human_design_authority(defined_centers: Dict[str, bool]) -> str:
    if defined_centers.get("Solar Plexus"):
        return "Emotional Solar Plexus"
    if defined_centers.get("Sacral"):
        return "Sacral"
    if defined_centers.get("Heart/Ego"):
        return "Ego"
    if defined_centers.get("G-Center"):
        return "Self-Projected"
    if defined_centers.get("Spleen"):
        return "Splenic"
    if defined_centers.get("Ajna") or defined_centers.get("Head"):
        return "Mental"
    return "None"


def _human_design_type(defined_centers: Dict[str, bool]) -> str:
    if not any(defined_centers.values()):
        return "Reflector"
    if defined_centers.get("Sacral"):
        motor_defined = any(
            defined_centers.get(center) for center in ["Heart/Ego", "Solar Plexus", "Root"]
        )
        if defined_centers.get("Throat") and motor_defined:
            return "Manifesting Generator"
        return "Generator"
    if defined_centers.get("Throat"):
        return "Manifestor"
    return "Projector"


def _human_design_strategy(type_name: str) -> str:
    return {
        "Generator": "Respond",
        "Manifesting Generator": "Respond, then Inform",
        "Projector": "Wait for the invitation",
        "Manifestor": "Inform before acting",
        "Reflector": "Wait a lunar cycle",
    }.get(type_name, "Unknown")


def _calc_design_attributes(birth_positions: List[Dict[str, object]], design_positions: List[Dict[str, object]]) -> Dict[str, object]:
    birth_sun_gate = _find_planet_position(birth_positions, "Sun")["gate"]
    design_sun_gate = _find_planet_position(design_positions, "Sun")["gate"]
    design_earth_gate = _find_planet_position(design_positions, "Earth")["gate"]
    active_gates = {p["gate"] for p in birth_positions + design_positions}
    defined_centers = _gates_to_centers(active_gates)
    active_channels = _active_channels(active_gates)
    definition = _definition_from_channels(defined_centers, active_channels)
    type_name = _human_design_type(defined_centers)
    strategy = _human_design_strategy(type_name)
    authority = _human_design_authority(defined_centers)
    birth_sun_position = _find_planet_position(birth_positions, "Sun")
    design_sun_position = _find_planet_position(design_positions, "Sun")
    design_earth_position = _find_planet_position(design_positions, "Earth")
    birth_line = line_from_longitude(birth_sun_position["longitude"])
    design_line = line_from_longitude(design_sun_position["longitude"])
    environment_line = line_from_longitude(design_earth_position["longitude"])
    digestion_label = DIGESTION_LABELS.get(design_line, f"Line {design_line}")
    environment_label = ENVIRONMENT_LABELS.get(environment_line, f"Line {environment_line}")
    design_sense_label = DESIGN_SENSE_LABELS.get(design_line, f"Line {design_line}")
    return {
        "type": type_name,
        "strategy": strategy,
        "inner_authority": authority,
        "profile": {
            "birth_sun_line": birth_line,
            "design_sun_line": design_line,
            "profile": f"{birth_line}/{design_line}",
        },
        "definition": definition,
        "defined_centers": [center for center, defined in defined_centers.items() if defined],
        "undefined_centers": [center for center, defined in defined_centers.items() if not defined],
        "active_channels": [
            {"name": channel["name"], "gates": channel["gates"], "centers": channel["centers"]}
            for channel in active_channels
        ],
        "digestion": {
            "line": design_line,
            "type": digestion_label,
            "description": f"{digestion_label} digestion",
        },
        "environment": {
            "line": environment_line,
            "type": environment_label,
            "description": f"{environment_label} environment",
        },
        "design_sense": {
            "line": design_line,
            "type": design_sense_label,
            "description": f"{design_sense_label} design sense",
        },
    }


def _download_ephemeris_file(filename: str, target_dir: str) -> None:
    url = SWISS_EPHEMERIS_GITHUB_RAW + filename
    request = Request(url, headers={"User-Agent": "Soul-Blueprint/1.0"})
    target_path = os.path.join(target_dir, filename)
    with urlopen(request, timeout=60) as response, open(target_path, "wb") as out_file:
        shutil.copyfileobj(response, out_file)


def _ensure_ephemeris_files(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    missing = [f for f in REQUIRED_EPHEMERIS_FILES if not os.path.exists(os.path.join(path, f))]
    if not missing:
        return
    print(f"Downloading missing Swiss Ephemeris files into {path}...")
    for filename in missing:
        try:
            _download_ephemeris_file(filename, path)
        except Exception as exc:
            raise RuntimeError(
                f"Unable to download required Swiss Ephemeris file '{filename}': {exc}. "
                "Set SWISS_EPHE_PATH to a valid ephemeris directory if automatic download fails."
            ) from exc


def set_ephemeris_path(path: Optional[str] = None) -> None:
    """Configure the Swiss Ephemeris data path."""
    if not path:
        path = os.getenv("SWISS_EPHE_PATH")
    if not path:
        path = LOCAL_EPHE_PATH
    _ensure_ephemeris_files(path)
    swe.set_ephe_path(path)


def timezone_offset_to_str(offset: float) -> str:
    sign = "+" if offset >= 0 else "-"
    absolute = abs(offset)
    hours = int(absolute)
    minutes = int(round((absolute - hours) * 60))
    if minutes:
        return f"UTC{sign}{hours}:{minutes:02d}"
    return f"UTC{sign}{hours}"


def parse_timezone(tz_value: Optional[str]) -> timezone:
    """Parse timezone input into a Python timezone object."""
    if not tz_value:
        return timezone.utc

    tz_value = tz_value.strip()
    if tz_value.upper().startswith("UTC"):
        offset_text = tz_value[3:]
        if not offset_text:
            return timezone.utc
        sign = 1 if offset_text.startswith("+") else -1
        offset_text = offset_text.lstrip("+-")
        hours, minutes = 0, 0
        if ":" in offset_text:
            hours_str, minutes_str = offset_text.split(":", 1)
            hours = int(hours_str)
            minutes = int(minutes_str)
        else:
            hours = int(offset_text)
        return timezone(sign * timedelta(hours=hours, minutes=minutes))

    # Accept raw numeric strings as offsets like -6 or 5.5
    try:
        offset = float(tz_value)
        return timezone(timedelta(hours=offset))
    except ValueError:
        pass

    try:
        return ZoneInfo(tz_value)
    except Exception as exc:
        raise ValueError(f"Unable to parse timezone '{tz_value}': {exc}") from exc


def to_utc_datetime(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    tz_value: Optional[str] = None,
) -> datetime:
    tz = parse_timezone(tz_value)
    local_dt = datetime(year, month, day, hour, minute, tzinfo=tz)
    return local_dt.astimezone(timezone.utc)


def julian_day_from_local(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    tz_value: Optional[str] = None,
) -> float:
    utc_dt = to_utc_datetime(year, month, day, hour, minute, tz_value)
    return swe.utc_to_jd(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour,
        utc_dt.minute,
        utc_dt.second,
    )[1]

US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
}


def normalize_location_string(location: str) -> str:
    return ", ".join(part.strip() for part in location.split(",") if part.strip())


def infer_country_hint(location: str, country_hint: Optional[str]) -> Optional[str]:
    if country_hint:
        return country_hint

    parts = [part.strip() for part in location.split(",") if part.strip()]
    if len(parts) >= 2 and parts[-1].upper() in US_STATE_CODES:
        return "USA"
    return None


def geocode_location(location: str, country_hint: Optional[str] = None) -> Tuple[float, float]:
    query = normalize_location_string(location)
    if not query:
        raise ValueError("Location string is empty")
    country = infer_country_hint(query, country_hint)
    if country:
        query = f"{query}, {country}"

    url = (
        "https://nominatim.openstreetmap.org/search?"
        + urlencode({"q": query, "format": "json", "limit": 1})
    )
    request = Request(
        url,
        headers={"User-Agent": "Soul-Blueprint/1.0 (user@example.com)"},
    )
    with urlopen(request, timeout=15) as response:
        data = json.load(response)

    if not data:
        raise ValueError(f"Unable to geocode location '{location}'")

    entry = data[0]
    return float(entry["lat"]), float(entry["lon"])


def resolve_location_to_latlon(location: str, country_hint: Optional[str] = None) -> Tuple[float, float]:
    return geocode_location(location, country_hint)


def normalize_longitude(longitude: float) -> float:
    return longitude % 360.0


def zodiac_position(longitude: float) -> Dict[str, object]:
    longitude = normalize_longitude(longitude)
    sign_index = int(longitude // 30.0)
    sign_name = SIGN_NAMES[sign_index]
    sign_degree = longitude - sign_index * 30.0
    degrees = int(sign_degree)
    minutes = int((sign_degree - degrees) * 60)
    seconds = int(((sign_degree - degrees) * 60 - minutes) * 60)
    return {
        "longitude": round(longitude, 6),
        "sign": sign_name,
        "sign_index": sign_index + 1,
        "degree": degrees,
        "minute": minutes,
        "second": seconds,
    }


def is_day_chart(jd_ut: float, latitude: float, longitude: float, sun_long: float, sun_lat: float, sun_dist: float) -> bool:
    alt = swe.azalt(
        jd_ut,
        swe.ECL2HOR,
        [longitude, latitude, 0.0],
        0,
        0,
        [sun_long, sun_lat, sun_dist],
    )[1]
    return alt >= 0.0


def part_of_fortune(ascendant: float, sun_long: float, moon_long: float, is_day: bool) -> float:
    if is_day:
        return normalize_longitude(ascendant + moon_long - sun_long)
    return normalize_longitude(ascendant - moon_long + sun_long)


def gate_from_longitude(longitude: float) -> int:
    longitude = normalize_longitude(longitude)
    index = int(math.floor((longitude + HD_GATE_OFFSET_DEGREES) / HD_GATE_WIDTH_DEGREES + 1e-12))
    index %= len(GATE_NUMBERS_BY_INDEX)
    return GATE_NUMBERS_BY_INDEX[index]


def _find_planet_position(positions: List[Dict[str, object]], planet_name: str) -> Dict[str, object]:
    for position in positions:
        if position["planet"] == planet_name:
            return position
    raise ValueError(f"Planet '{planet_name}' not found in positions")


def incarnation_cross(birth_positions: List[Dict[str, object]], design_positions: List[Dict[str, object]]) -> Dict[str, object]:
    birth_sun = _find_planet_position(birth_positions, "Sun")
    birth_earth = _find_planet_position(birth_positions, "Earth")
    design_sun = _find_planet_position(design_positions, "Sun")
    design_earth = _find_planet_position(design_positions, "Earth")
    gates = [
        birth_sun["gate"],
        birth_earth["gate"],
        design_sun["gate"],
        design_earth["gate"],
    ]
    return {
        "birth_sun": {"planet": "Sun", "gate": birth_sun["gate"], "zodiac": birth_sun["zodiac"]},
        "birth_earth": {"planet": "Earth", "gate": birth_earth["gate"], "zodiac": birth_earth["zodiac"]},
        "design_sun": {"planet": "Sun", "gate": design_sun["gate"], "zodiac": design_sun["zodiac"]},
        "design_earth": {"planet": "Earth", "gate": design_earth["gate"], "zodiac": design_earth["zodiac"]},
        "gates": [
            {"planet": "Birth Sun", "gate": birth_sun["gate"]},
            {"planet": "Birth Earth", "gate": birth_earth["gate"]},
            {"planet": "Design Sun", "gate": design_sun["gate"]},
            {"planet": "Design Earth", "gate": design_earth["gate"]},
        ],
        "unique_gates": sorted(set(gates)),
    }


def planet_positions(jd_ut: float, include_special: bool = False) -> List[Dict[str, object]]:
    positions = []
    node_longitude = None
    sun_longitude = None

    for name, body in PLANET_NAMES:
        pos, _ = swe.calc_ut(jd_ut, body)
        longitude = normalize_longitude(pos[0])
        positions.append(
            {
                "planet": name,
                "longitude": round(longitude, 6),
                "zodiac": zodiac_position(longitude),
                "gate": gate_from_longitude(longitude),
            }
        )
        if name == "North Node":
            node_longitude = longitude
        if name == "Sun":
            sun_longitude = longitude

    if sun_longitude is not None:
        earth_longitude = normalize_longitude(sun_longitude + 180.0)
        positions.append(
            {
                "planet": "Earth",
                "longitude": round(earth_longitude, 6),
                "zodiac": zodiac_position(earth_longitude),
                "gate": gate_from_longitude(earth_longitude),
            }
        )

    if node_longitude is not None:
        south_node_longitude = normalize_longitude(node_longitude + 180.0)
        positions.append(
            {
                "planet": "South Node",
                "longitude": round(south_node_longitude, 6),
                "zodiac": zodiac_position(south_node_longitude),
                "gate": gate_from_longitude(south_node_longitude),
            }
        )

    if include_special:
        for name, body in SPECIAL_PLANETARY_POINTS:
            pos, _ = swe.calc_ut(jd_ut, body)
            positions.append(
                {
                    "planet": name,
                    "longitude": round(normalize_longitude(pos[0]), 6),
                    "zodiac": zodiac_position(pos[0]),
                    "gate": gate_from_longitude(pos[0]),
                }
            )
    return positions


def whole_sign_houses(jd_ut: float, latitude: float, longitude: float) -> Dict[str, object]:
    cusps, ascmc = swe.houses(jd_ut, latitude, longitude, b"W")
    return {
        "cusps": [round(normalize_longitude(deg), 6) for deg in cusps],
        "ascendant": round(normalize_longitude(ascmc[0]), 6),
        "mc": round(normalize_longitude(ascmc[1]), 6),
        "vertex": round(normalize_longitude(ascmc[3]), 6),
    }


def human_design_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    latitude: float,
    longitude: float,
    tz_value: Optional[str] = None,
    design_offset_days: int = 88,
) -> Dict[str, object]:
    set_ephemeris_path()
    birth_jd = julian_day_from_local(year, month, day, hour, minute, tz_value)
    birth_positions = planet_positions(birth_jd)
    birth_positions_with_extras = list(birth_positions)
    birth_positions_with_extras.extend(planet_positions(birth_jd, include_special=True)[len(birth_positions):])
    houses = whole_sign_houses(birth_jd, latitude, longitude)

    sun_pos, _ = swe.calc_ut(birth_jd, swe.SUN)
    moon_pos, _ = swe.calc_ut(birth_jd, swe.MOON)
    day_chart = is_day_chart(birth_jd, latitude, longitude, sun_pos[0], sun_pos[1], sun_pos[2])
    fortune_long = part_of_fortune(houses["ascendant"], sun_pos[0], moon_pos[0], day_chart)
    birth_positions_with_extras.append(
        {
            "planet": "Part of Fortune",
            "longitude": round(normalize_longitude(fortune_long), 6),
            "zodiac": zodiac_position(fortune_long),
            "gate": gate_from_longitude(fortune_long),
        }
    )
    birth_positions_with_extras.append(
        {
            "planet": "Vertex",
            "longitude": houses["vertex"],
            "zodiac": zodiac_position(houses["vertex"]),
            "gate": gate_from_longitude(houses["vertex"]),
        }
    )

    birth_utc = to_utc_datetime(year, month, day, hour, minute, tz_value)
    design_date = birth_utc - timedelta(days=design_offset_days)
    design_jd = swe.utc_to_jd(
        design_date.year,
        design_date.month,
        design_date.day,
        design_date.hour,
        design_date.minute,
        design_date.second,
    )[1]
    design_positions = planet_positions(design_jd, include_special=True)

    cross = incarnation_cross(birth_positions, design_positions)
    derived = _calc_design_attributes(birth_positions, design_positions)
    return {
        "birth": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "timezone": tz_value or "UTC",
            "utc_datetime": birth_utc.isoformat(),
            "planet_positions": birth_positions_with_extras,
            "whole_sign_houses": houses,
        },
        "design": {
            "date": design_date.date().isoformat(),
            "utc_datetime": design_date.isoformat(),
            "planet_positions": design_positions,
        },
        "summary": {
            "conscious_gates": [
                {"planet": p["planet"], "gate": p["gate"]} for p in birth_positions
            ],
            "unconscious_gates": [
                {"planet": p["planet"], "gate": p["gate"]} for p in design_positions
            ],
            "incarnation_cross": cross,
            "derived": derived,
        },
    }


def human_design_chart_from_location(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    location: str,
    tz_value: Optional[str] = None,
    country_hint: Optional[str] = None,
    design_offset_days: int = 88,
) -> Dict[str, object]:
    latitude, longitude = resolve_location_to_latlon(location, country_hint)
    return human_design_chart(
        year,
        month,
        day,
        hour,
        minute,
        latitude,
        longitude,
        tz_value,
        design_offset_days,
    )


def human_design_chart_from_intake(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    place_of_birth: str,
    timezone_offset: Optional[float] = None,
    timezone_name: Optional[str] = None,
    country_hint: Optional[str] = None,
    design_offset_days: int = 88,
) -> Dict[str, object]:
    if timezone_name:
        tz_value = timezone_name
    elif timezone_offset is not None:
        tz_value = timezone_offset_to_str(timezone_offset)
    else:
        tz_value = "UTC"

    latitude, longitude = resolve_location_to_latlon(place_of_birth, country_hint)
    return human_design_chart(
        year,
        month,
        day,
        hour,
        minute,
        latitude,
        longitude,
        tz_value,
        design_offset_days,
    )


def format_chart(chart: Dict[str, object]) -> str:
    lines = ["Human Design chart results:"]
    birth = chart["birth"]
    lines.append(
        f"Birth: {birth['year']}-{birth['month']:02d}-{birth['day']:02d} {birth['hour']:02d}:{birth['minute']:02d} ({birth['timezone']})"
    )
    lines.append("\nWhole sign house cusps:")
    for i, cusp in enumerate(birth["whole_sign_houses"]["cusps"], start=1):
        lines.append(f"  House {i}: {cusp:.6f}°")
    lines.append("\nBirth chart gates:")
    for position in birth["planet_positions"]:
        lines.append(
            f"  {position['planet']}: {position['zodiac']['sign']} {position['zodiac']['degree']}°{position['zodiac']['minute']}' gate {position['gate']}"
        )
    lines.append("\nDesign chart date: " + chart["design"]["date"])
    lines.append("Design chart gates:")
    for position in chart["design"]["planet_positions"]:
        lines.append(
            f"  {position['planet']}: {position['zodiac']['sign']} {position['zodiac']['degree']}°{position['zodiac']['minute']}' gate {position['gate']}"
        )
    lines.append("\nIncarnation Cross:")
    for entry in chart["summary"]["incarnation_cross"]["gates"]:
        lines.append(f"  {entry['planet']}: Gate {entry['gate']}")

    derived = chart["summary"]["derived"]
    lines.append("\nDerived Human Design:")
    lines.append(f"  Type: {derived['type']}")
    lines.append(f"  Strategy: {derived['strategy']}")
    lines.append(f"  Inner Authority: {derived['inner_authority']}")
    lines.append(f"  Profile: {derived['profile']['profile']}")
    lines.append(f"  Definition: {derived['definition']['type']}")
    lines.append(f"  Defined Centers: {', '.join(derived['defined_centers'])}")
    lines.append(f"  Undefined Centers: {', '.join(derived['undefined_centers'])}")
    lines.append(f"  Digestion: {derived['digestion']['type']} (line {derived['digestion']['line']})")
    lines.append(f"  Environment: {derived['environment']['type']} (line {derived['environment']['line']})")
    lines.append(f"  Design Sense: {derived['design_sense']['type']} (line {derived['design_sense']['line']})")
    lines.append("\nActive Channels:")
    for channel in derived["active_channels"]:
        lines.append(f"  {channel['name']}: {channel['gates'][0]}-{channel['gates'][1]}")
    return "\n".join(lines)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Compute whole sign astrology and Human Design chart data.")
    parser.add_argument("--date", required=True, help="Birth date in YYYY-MM-DD format")
    parser.add_argument("--time", required=True, help="Birth time in HH:MM (24-hour) format")
    parser.add_argument(
        "--timezone",
        required=False,
        default=None,
        help="Timezone name or offset, for example 'UTC-6' or 'America/Denver'",
    )
    parser.add_argument(
        "--timezone-offset",
        required=False,
        type=float,
        default=None,
        help="Numeric timezone offset from UTC, for example -6 or 5.5",
    )
    parser.add_argument("--latitude", type=float, required=False, help="Birth latitude in decimal degrees")
    parser.add_argument("--longitude", type=float, required=False, help="Birth longitude in decimal degrees")
    parser.add_argument(
        "--location",
        required=False,
        help="Birth location as 'City, State' or 'City, State, Country'",
    )
    parser.add_argument(
        "--country",
        required=False,
        default=None,
        help="Optional country hint for location lookup",
    )
    parser.add_argument(
        "--ephe-path",
        required=False,
        default=None,
        help="Optional path to Swiss Ephemeris data files",
    )
    args = parser.parse_args()

    if args.ephe_path:
        set_ephemeris_path(args.ephe_path)

    year, month, day = [int(part) for part in args.date.split("-")]
    hour, minute = [int(part) for part in args.time.split(":")]

    if args.latitude is None or args.longitude is None:
        if not args.location:
            parser.error("Either --latitude and --longitude or --location must be provided")
        latitude, longitude = resolve_location_to_latlon(args.location, args.country)
    else:
        latitude, longitude = args.latitude, args.longitude

    if args.timezone is not None:
        tz_value = args.timezone
    elif args.timezone_offset is not None:
        tz_value = timezone_offset_to_str(args.timezone_offset)
    else:
        tz_value = "UTC"

    chart = human_design_chart(
        year,
        month,
        day,
        hour,
        minute,
        latitude,
        longitude,
        tz_value,
    )
    print(format_chart(chart))
