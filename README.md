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

## Example curl
```bash
curl http://127.0.0.1:8080/health
curl "http://127.0.0.1:8080/sources/magister/rooster?dateFrom=2026-03-17&dateTill=2026-03-24"
curl http://127.0.0.1:8080/sources/voetbal/events
curl -X POST http://127.0.0.1:8080/plan/export/ical \
  -H 'Content-Type: application/json' \
  -d '{"generatedAt":"2026-03-13T00:00:00Z","blocks":[]}'
```

## Cloud
- Deployed on Cloud Run
- Use env vars for tokens (no secrets in git)

## Firebase / Firestore
- Firestore (native) enabled in GCP project
- Set `GOOGLE_APPLICATION_CREDENTIALS` or use Workload Identity on Cloud Run
- Schema: `docs/firestore-schema.md`
- Seed workflow: `.github/workflows/seed-firestore.yml`

## Magister helpers
- `scripts/fetch_huiswerk_7d.sh` (huiswerk/inhoud uit afspraken)

## OpenAPI Spec
See `docs/openapi.yaml`.
