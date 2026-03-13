# Design

- Extend `src/app.py` with stub implementations for all OpenAPI endpoints.
- Add Pydantic models mirroring `docs/openapi.yaml` schemas.
- For external sources, return placeholder JSON with clear `source` labels.
- For iCal export, return `text/calendar` with a minimal calendar header.
