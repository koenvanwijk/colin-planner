# Colin Planner (MVP)

Personal assistant/planner for a VWO4 student. Pulls data from multiple sources and produces a weekly plan.

## Goals
- Fetch: Magister (rooster/toetsen), voetbal.nl (training/wedstrijden)
- Plan: produce blocks for school, work, study, sport, rest
- Output: WhatsApp notification + JSON/iCal

## Scope (MVP)
- Python backend (FastAPI)
- Manual config of fixed activities (work, voetbal)
- Magister + voetbal.nl as external sources (best-effort)
- Generate a weekly plan JSON + iCal
- Send WhatsApp message via provider API (Twilio/MessageBird)

## Non-Goals (MVP)
- Full automatic WhatsApp scraping (not supported / against ToS)
- Real-time replanning based on live chat

## Quick start
```bash
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8080
```

## Cloud
- Works on Render/Fly/VM
- Use env vars for tokens (no secrets in git)

## OpenAPI Spec
See `docs/openapi.yaml`.
