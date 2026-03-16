# Specs

## Functional
- Fetch roster (7-day window) reliably
- Extract homework/lesson content (Inhoud/Opmerking)
- Normalize to planner JSON schema

## Robustness
- Configurable school tenant (subdomain)
- Automatic personId resolution
- Error reporting when tenant/login changes

## Security/Compliance
- Credentials stored only in env/secrets
- No credentials logged
- Use test account if available
