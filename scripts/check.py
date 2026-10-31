"""Check SolverX public endpoints and update data/status.json and data/daily.json."""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SERVICES = [
    {"id": "studio", "name": "SolverX Studio", "host": "app.solverx.ai", "url": "https://app.solverx.ai"},
    {"id": "api", "name": "API", "host": "api.solverx.ai", "url": "https://api.solverx.ai/health"},
    {"id": "auth", "name": "Sign-in", "host": "auth.solverx.ai", "url": "https://auth.solverx.ai/debug/healthz"},
    {"id": "website", "name": "Website", "host": "www.solverx.ai", "url": "https://www.solverx.ai"},
]
TIMEOUT_S = 15
KEEP_DAYS = 90
DATA = Path(__file__).resolve().parent.parent / "data"


def probe(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SolverX-Status/1.0"})
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception:
        code = 0
    ms = int((time.monotonic() - start) * 1000)
    return 200 <= code < 400, code, ms


def check(url):
    up, code, ms = probe(url)
    if not up:
        # One retry so a single dropped request is not reported as an outage.
        time.sleep(5)
        up, code, ms = probe(url)
    return up, code, ms


def load(name, default):
    path = DATA / name
    return json.loads(path.read_text()) if path.exists() else default


def main():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    today = now.date().isoformat()
    cutoff = (now.date() - timedelta(days=KEEP_DAYS - 1)).isoformat()

    previous = {s["id"]: s for s in load("status.json", {}).get("services", [])}
    daily = load("daily.json", {})

    services = []
    for svc in SERVICES:
        up, code, ms = check(svc["url"])
        prev = previous.get(svc["id"])
        since = prev["since"] if prev and prev["up"] == up else now.isoformat()
        services.append({"id": svc["id"], "name": svc["name"], "host": svc["host"],
                         "up": up, "code": code, "ms": ms, "since": since})

        days = daily.setdefault(svc["id"], {})
        checks, ok = days.get(today, [0, 0])
        days[today] = [checks + 1, ok + (1 if up else 0)]
        for day in [d for d in days if d < cutoff]:
            del days[day]

    DATA.mkdir(exist_ok=True)
    (DATA / "status.json").write_text(json.dumps({"updated": now.isoformat(), "services": services}, indent=2) + "\n")
    (DATA / "daily.json").write_text(json.dumps(daily, indent=2, sort_keys=True) + "\n")
    for s in services:
        print(f"{s['id']:8} {'UP' if s['up'] else 'DOWN':4} {s['code']} {s['ms']}ms")


if __name__ == "__main__":
    main()
