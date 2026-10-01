# Architecture Overview

## Runtime flow

1. Frontend form (`client`) collects business profile.
2. Next.js API route proxies request to FastAPI backend.
3. FastAPI validates input schema (Pydantic).
4. Agent orchestrator executes:
   - deterministic registration evaluation from KB (`server/data/registrations.json`)
   - optional GST/PAN verification tools (mock/sandbox/live)
   - optional LLM wording enrichment (schema-constrained)
5. Action layer executes:
   - markdown, csv, pdf generation
   - Google Sheets append
   - SMTP email send
6. API persists generated artifacts to `server/artifacts` and returns URLs.

## Deterministic vs AI-generated

- Deterministic:
  - applicability statuses
  - required docs, links, source references
  - missing-info detection
- AI-generated (optional):
  - profile summary wording
  - action sequencing text

## Safety controls

- request size limit (`MAX_REQUEST_BYTES`)
- per-IP in-memory rate limit (`RATE_LIMIT_REQUESTS_PER_MINUTE`)
- configurable CORS (`CORS_ALLOW_ORIGINS`)
- verification mode (`VERIFICATION_MODE=mock|sandbox|live`)
