import argparse
import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
import urllib.request
import urllib.error

from astrology_humandesign import (
    human_design_chart,
    human_design_chart_from_intake,
    set_ephemeris_path,
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


def _run_anthropic_generation(prompt: str, job_id: str) -> None:
    """Background thread: call Anthropic API and store result in job dict."""
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set on the server")

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

        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if path in TEMPLATE_ROUTES:
            filename = TEMPLATE_ROUTES[path]
            file_path = Path(__file__).parent / filename
            try:
                content = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                for k, v in CORS_HEADERS:
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self._send_json(404, {"error": f"{filename} not found"})
            return

        if path.startswith("/job-status/"):
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
            return

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

        elif path == "/start-generation":
            prompt = payload.get("prompt", "")
            if not prompt:
                self._send_json(400, {"error": "'prompt' is required"})
                return
            job_id = str(uuid.uuid4())
            with _JOBS_LOCK:
                _JOBS[job_id] = {"status": "running"}
            t = threading.Thread(
                target=_run_anthropic_generation,
                args=(prompt, job_id),
                daemon=True,
            )
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
                year,
                month,
                day,
                hour,
                minute,
                float(latitude),
                float(longitude),
                tz_value,
                88,
            )
        elif location:
            chart = human_design_chart_from_intake(
                year,
                month,
                day,
                hour,
                minute,
                location,
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
                "sun": swe.SUN,
                "moon": swe.MOON,
                "mercury": swe.MERCURY,
                "venus": swe.VENUS,
                "mars": swe.MARS,
                "jupiter": swe.JUPITER,
                "saturn": swe.SATURN,
                "uranus": swe.URANUS,
                "neptune": swe.NEPTUNE,
                "pluto": swe.PLUTO,
                "northnode": swe.MEAN_NODE,
                "chiron": swe.CHIRON,
            }

            retrograde_map = {}
            for name, pid in planet_ids.items():
                result, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
                speed = result[3]
                retrograde_map[name] = speed < 0

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
    parser.add_argument("--port", type=int, default=8000, help="Port for the local API server")
    parser.add_argument(
        "--ephe-path",
        required=False,
        default=None,
        help="Optional path to Swiss Ephemeris data files",
    )
    args = parser.parse_args()
    run_server(args.port, args.ephe_path)
