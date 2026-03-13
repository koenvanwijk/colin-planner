# Specs

## Endpoints
- GET `/health` → `{ ok: true }`
- GET `/sources/magister/rooster?dateFrom&dateTill` → JSON placeholder
- GET `/sources/voetbal/events` → JSON placeholder
- POST `/plan/build` → returns PlanResponse
- POST `/plan/export/ical` → returns text/calendar (placeholder)
- POST `/notifications/whatsapp` → returns `{ sent: true }`

## Validation
- FastAPI routes exist and respond with expected shapes
- Responses align with OpenAPI schema
