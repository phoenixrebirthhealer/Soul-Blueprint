# Soul-Blueprint

This repository now includes a Python module for computing:
- astrology whole sign houses using PySwisseph
- Human Design gate activations for birth and design date

## Usage

1. Install dependencies:

```bash
pip install pyswisseph
```

2. Make sure Swiss Ephemeris data is available and set the path if needed:

```bash
export SWISS_EPHE_PATH=/path/to/ephemeris
```

If no path is provided, the code will automatically download the required ephemeris files into `./ephe` on first run.

3. Run the script with coordinates:

```bash
python astrology_humandesign.py \
  --date 1983-04-09 \
  --time 02:17 \
  --timezone-offset -6 \
  --latitude 32.7 \
  --longitude -103.1333
```

Or run the script with a city/state location string and timezone offset:

```bash
python astrology_humandesign.py \
  --date 1983-04-09 \
  --time 02:17 \
  --timezone-offset -6 \
  --location "Hobbs, NM"
```

## Local API

Run the local API server:

```bash
python local_api.py --port 8000
```

Send a POST request to `/chart` with JSON:

```bash
curl -X POST http://127.0.0.1:8000/chart \
  -H "Content-Type: application/json" \
  -d '{
    "date": "1983-04-09",
    "time": "02:17",
    "timezoneOffset": -6,
    "location": "Hobbs, NM"
  }'
```

Or send coordinates directly:

```bash
curl -X POST http://127.0.0.1:8000/chart \
  -H "Content-Type: application/json" \
  -d '{
    "date": "1983-04-09",
    "time": "02:17",
    "timezoneOffset": -6,
    "latitude": 32.7,
    "longitude": -103.1333
  }'
```

The API responds with JSON containing the birth chart, design chart, and gate summary.

## Notes

- The script uses the birth date and local time to compute a UTC Julian Day.
- It automatically computes a Human Design design date 88 days before birth.
- The birth chart now also includes Chiron, Black Moon Lilith, Earth, South Node, Part of Fortune, and Vertex in `birth.planet_positions`.
- The node gate uses True North Node, which is the standard Human Design calculation.
- Gate lookups now use the correct Human Design zodiac wheel order with the proper 64-gate offset.
- The API now includes Incarnation Cross gate detection from birth and design Sun/Earth positions.
- The HD gate wheel offset has been tuned to match verified 61/62 boundary behavior.
- You may provide either `--latitude` and `--longitude` or `--location` (for example `City, State`).
- You may also provide `--timezone-offset` instead of a timezone name.
- When using `--location`, the script will query a geocoding service to resolve coordinates, so network access is required.
- If your intake form already resolves a location suggestion to `lat`/`lon`, pass those coordinates directly for the most accurate result.
