# Proposal: Implement endpoints from OpenAPI schema

## Why
The OpenAPI spec defines endpoints that are not yet fully implemented in the FastAPI app. We want the API to match the documented schema so clients can rely on it.

## Scope
- Implement endpoints in `docs/openapi.yaml` in the FastAPI app
- Add request/response models that align with schema
- Return placeholder data where integrations are not yet wired

## Non-Goals
- Full Magister/voetbal.nl integration
- Production-grade auth
