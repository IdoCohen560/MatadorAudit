#!/usr/bin/env python3
"""Health check script for MatadorAudit Streamlit app.
Pings the app URL to prevent Streamlit Cloud from sleeping.
Run via cron every 3 hours: 0 */3 * * * python3 /path/to/health_check.py
"""

import urllib.request
import urllib.error
import sys
from datetime import datetime

URLS = [
    "https://matadoraudit.streamlit.app",
    "https://matadoraudit.netlify.app",
]


def ping(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "MatadorAudit-HealthCheck/1.0")
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            print(f"[{datetime.now().isoformat()}] {url} -> {status}")
            return 200 <= status < 400
    except urllib.error.HTTPError as e:
        # Streamlit returns 303 redirects on wake — that means it's alive
        if e.code in (301, 302, 303, 307, 308):
            print(f"[{datetime.now().isoformat()}] {url} -> {e.code} (redirect, app is alive)")
            return True
        print(f"[{datetime.now().isoformat()}] {url} -> FAIL: {e.code}")
        return False
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] {url} -> FAIL: {e}")
        return False


if __name__ == "__main__":
    results = [ping(url) for url in URLS]
    if not all(results):
        sys.exit(1)
