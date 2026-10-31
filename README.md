# SolverX Status

Public status page for SolverX services: https://status.solverx.ai

- `scripts/check.py` checks each service every 10 minutes (GitHub Actions schedule) and updates `data/status.json` (current state) and `data/daily.json` (daily availability, 90 days).
- `data/incidents.json` lists incidents shown on the page. Add an entry when an incident affects customers:

```json
[{"date": "2026-11-01", "title": "API errors", "status": "Resolved",
  "updates": [{"time": "10:20 KST", "text": "Investigating elevated error rates."},
              {"time": "10:45 KST", "text": "Fixed and monitoring."}]}]
```

Services and their health URLs are listed in `SERVICES` in `scripts/check.py`.
