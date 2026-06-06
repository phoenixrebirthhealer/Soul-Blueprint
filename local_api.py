import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional

print("local_api.py: starting imports", flush=True)
try:
    from astrology_humandesign import (
        human_design_chart,
        human_design_chart_from_intake,
        set_ephemeris_path,
    )
    print("local_api.py: astrology_humandesign OK", flush=True)
except Exception as _import_exc:
    import traceback
    print(f"FATAL IMPORT ERROR: {_import_exc}", flush=True)
    traceback.print_exc()
    sys.exit(1)

CORS_HEADERS = [
    ("Access-Control-Allow-Origin", "*"),
    ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
    ("Access-Control-Allow-Headers", "Content-Type, Authorization"),
]

def _parse_time(time_str: str):
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
        if path in ("/health", "/"):
            self._send_json(200, {"status": "ok"})
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

        return chart

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server(port: int, ephe_path: Optional[str]) -> None:
    print(f"run_server called with port={port}", flush=True)
    set_ephemeris_path(ephe_path)
    print(f"ephemeris path set, binding HTTPServer on port {port}", flush=True)
    try:
        server = HTTPServer(("", port), LocalAPIHandler)
    except Exception as e:
        print(f"FATAL: HTTPServer bind failed on port {port}: {e}", flush=True)
        raise
    print(f"Local API running on http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    parser.add_argument("--ephe-path", required=False, default=None)
    args = parser.parse_args()
    run_server(args.port, args.ephe_path)
Commit that, let Railway redeploy, and confirm /health works. Once it does we build back up from there one piece at a time.You've used 75% of your weekly limitGet more usageSonnet 4.6 LowClaude is AI and can make mistakes. Please double-check responses.ShareContent// SoulBlueprintAdmin.jsx
// Phoenix Rebirth | SoulReady
// Admin only — Christina's control center
// Auto-calculate + manual entry + reading generation + Tier 2 prep

import { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { runNumerologyCalculation pasted// soulBlueprintApi.js
// Phoenix Rebirth | SoulReady
// Calls external Soul Blueprint API for astrology + human design calculations.
// API: https://soul-blueprint-production.up.railway.app/chart
// POST { date: "YYYY-MM-DD", time: "HH:MM", latitude, longitude, timezone }

import { base44 } fpasted// SoulBlueprintAdmin.jsx
// Phoenix Rebirth | SoulReady
// Admin only — Christina's control center
// Auto-calculate + manual entry + reading generation + Tier 2 prep

import { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { runNumerologyCalculation pasted// SoulBlueprintAdmin.jsx
// Phoenix Rebirth | SoulReady
// Admin only — Christina's control center
// Auto-calculate + manual entry + reading generation + Tier 2 prep

import { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { runNumerologyCalculation pastedconst handleGenerateNameFrequency = async () => {
  if (!readingRecord) return;
  setNfLoading(true); setNfStatus('Fetching template...');
  try {
    const tr = await fetch('https://soul-blueprint-production.up.railway.app/name-frequency-template');
    if (!tr.ok) throw new Error('Template fepasted// SoulBlueprintAdmin.jsx
// Phoenix Rebirth | SoulReady
// Admin only — Christina's control center
// Auto-calculate + manual entry + reading generation + Tier 2 prep

import { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { runNumerologyCalculation pastedimport argparse
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

fpasted<?php
require_once __DIR__ . '/includes/admin-auth.php';
admin_require_login();

header('Content-Type: application/json');

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid request']);
    expasted<?php
require_once __DIR__ . '/includes/admin-auth.php';
require_once __DIR__ . '/../includes/auth.php';
admin_require_login();

// Hebrew calc — load if available
if (file_exists(__DIR__ . '/../includes/hebrew-calc.php')) {
    include __DIR__ . '/../includes/hebrew-calc.php';
}

// Numerpasted<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Soul Blueprint | soulReady</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&family=Cormorant+Garamond:ital,wght@0,400pastedimport argparse
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

fpastedimport argparse
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

fpastedimport argparse
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

ipastedimport argparse
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

ipasted2026-06-06T01:13:38.983832479Z [err]    File "/app/local_api.py", line 922
2026-06-06T01:13:38.983835538Z [err]      Claude finished the responseYou said: Based on this information rmation that you gave me, can you please give me a list (like 5 or 6 that people wouldn't THINK to use for that specifipastedimport argparse
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

import sys
pripastedimport argparse
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

import sys
pripastedimport argparse
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

import sys
pripastedimport argparse
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

import sys
pripasted
