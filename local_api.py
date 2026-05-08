import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional

from astrology_humandesign import (
    human_design_chart,
    human_design_chart_from_intake,
    set_ephemeris_path,
)


class LocalAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/chart":
            self._send_json(404, {"error": "use POST /chart"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON body"})
            return

        try:
            chart = self._build_chart(payload)
            self._send_json(200, chart)
        except Exception as exc:
            self._send_json(400, {"error": str(exc)})

    def _build_chart(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        date = payload.get("date")
        time = payload.get("time")
        if not date or not time:
            raise ValueError("'date' and 'time' are required")

        year, month, day = [int(part) for part in date.split("-")]
        hour, minute = [int(part) for part in time.split(":")]

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
