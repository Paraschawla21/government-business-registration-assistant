# Demo Checklist (Exact Script)

Use this script for interviews, hackathon judging, and portfolio walkthroughs.

## 0) Pre-demo setup (2-3 mins)

1. Start backend:

```bash
cd server
source env/bin/activate
set -a
source .env
set +a
uvicorn api:app --reload --port 8000
```

2. Start frontend:

```bash
cd client
npm run dev
```

3. Open app: `http://localhost:3000`

4. Open backend docs (optional): `http://127.0.0.1:8000/docs`

## 1) Recommended demo env values

For stable demo without external dependency failures, use:

```env
VERIFICATION_MODE=mock
AGENT_ENABLE_LLM=false
MAX_REQUEST_BYTES=65536
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

For live API demo, switch mode and configure credentials:

```env
VERIFICATION_MODE=sandbox
SETU_BEARER_TOKEN=...
SETU_GST_VERIFY_URL=https://api.setu.co/data/gst/{gstin}
SETU_PAN_VERIFY_URL=https://api.setu.co/data/pan/{pan}
```

## 2) Primary demo input (copy/paste)

- Business Type: `Private Limited`
- Industry: `Information Technology`
- State: `Maharashtra`
- City: `Pune`
- Number of Employees: `12`
- Turnover: `40 Lakhs - 1 Crore`
- Core Activity: `Building and exporting software products for SMBs`
- Operations: `Both Online & Offline`
- GSTIN (optional): `27ABCDE1234F1Z5`
- PAN (optional): `ABCDE1234F`

## 3) What to show in sequence

1. Submit form and highlight schema-driven validation.
2. Show registration cards with statuses:
   - Applicable / More Info Required / Not Relevant
3. Open one card and explain:
   - required docs
   - missing info
   - official link
4. Show "Data sources used" block:
   - KB source
   - mock/sandbox/live API source labels
5. Show generated outputs section:
   - download markdown
   - download CSV tracker
   - download PDF report
   - open sheet link (if configured)
6. Mention fallback behavior:
   - if APIs fail, deterministic result still returned
   - output schema remains stable

## 4) Optional robustness demos

### A) Validation failure
- Enter invalid GSTIN/PAN format and submit.
- Show user-facing validation errors.

### B) Rate limiting
- Temporarily set `RATE_LIMIT_REQUESTS_PER_MINUTE=1`.
- Submit twice quickly.
- Show HTTP 429 behavior.

### C) Request size control
- Paste very large activity text.
- Show backend `413` guard (if payload threshold exceeded).

## 5) Suggested narration (30 sec)

"This system uses a deterministic government-registration knowledge base for
applicability decisions, optional verification APIs for GST/PAN, and an
orchestrator that can use LLM only for wording. It avoids hallucination by
keeping core decisions deterministic and always returning a structured,
fallback-safe output with actionable artifacts."

## 6) Post-demo verification commands

```bash
# backend
cd server && python3 -m pytest

# frontend
cd client && npm test && npm run build
```
