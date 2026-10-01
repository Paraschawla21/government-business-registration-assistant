# Government Business Registration Assistant

[![Frontend Build](https://img.shields.io/badge/frontend-build-passing-brightgreen)](#running-locally)
[![Backend Tests](https://img.shields.io/badge/backend-tests-passing-brightgreen)](#tests)
[![License](https://img.shields.io/badge/license-MIT-blue)](#disclaimer)

An AI Agent workflow that helps first-time entrepreneurs in India understand which
government registrations, licences, and approvals may apply to their business —
based on business type, industry, location, employee count, turnover, and
activity — and generates an actionable, step-by-step setup checklist.

## Quick Start (Recruiter-Friendly)

```bash
# 1) Backend
cd server
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
set -a && source .env && set +a
uvicorn api:app --reload --port 8000

# 2) Frontend (new terminal)
cd client
npm install
npm run dev
```

Open `http://localhost:3000` and submit a sample business profile to see:

- registration applicability decisions
- required docs and missing info
- official links and source logging
- downloadable markdown/csv/pdf outputs

> Status: early-stage / actively being built. This repo currently contains the
> business-profile intake UI and the backend scaffolding (FastAPI + local LLM via
> Ollama, structured/schema-validated output). The rule-engine, government
> data/API integrations, and action layer (report/sheet/email generation)
> described below are the next milestones — see [Roadmap](#roadmap).

## Why this project

Business registration requirements in India vary by business type, industry,
state, city, employee count, and turnover — making it hard for a first-time
entrepreneur to know what applies to them, what documents are needed, and where
to apply. This project aims to turn that into a guided, AI-assisted workflow:

```
Business Info → AI Agent → Government Data/API → Reasoning → Decision → Action → Outcome
```

## MVP scope (frozen)

This section defines what version `v1` must deliver end-to-end.

### MVP output: one personalized business setup report

For each submitted business profile, the system will produce one structured report with:

- Potentially relevant registrations and licences
- Applicability status per item:
  - `Applicable`
  - `More Info Required`
  - `Not Relevant`
- Why the item is classified that way
- Required documents and information (from verified sources)
- Missing inputs required to make a confident decision
- Official application/source links
- Suggested sequence of actions (recommended next steps)
- Verification notes for items that depend on state-specific or case-specific rules

### Supported geography (MVP)

- Country coverage: India-wide (baseline)
- State handling: limited state-specific logic in MVP
  - The system will apply state-level rules only where they are explicitly modeled and source-verified
  - For uncovered state-level rules, output will default to `More Info Required` with a verification note

### Out of scope for MVP

- Full legal advisory or legal representation
- Complete automation for every state/municipal licensing edge case
- Guarantee of approval timelines, fees, or processing outcomes

### Design principle: don't hallucinate compliance facts

Registration eligibility rules, fees, and required documents must come from a
verified knowledge base / official government sources — not be invented by the
LLM. The agent is being designed so the LLM only reasons over facts fetched
from a controlled data source or live government API, and clearly flags when
more information or manual verification is required, rather than guessing.

## Tech stack

- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, Pydantic
- **AI/LLM:** Ollama (local LLM), JSON-schema-constrained structured output
- **Integrations:** Setu GST/PAN verification, Google Sheets, SMTP email
- **Actions:** Markdown/CSV/PDF report generation, tracker append, email dispatch

## Repo structure

```
client/   Next.js frontend — business profile intake form + results view
server/   FastAPI backend — deterministic evaluator + optional live verification
```

## Knowledge base and deterministic evaluation

This project now uses a structured registration knowledge base at:

- `server/data/registrations.json`
- `server/data/india_registration_portals.json` (state-wise S&E/PT/Trade portal routing)

Each entry includes:

- registration name
- issuing authority
- official portal URL
- source reference URL and source reference date
- applicability conditions
- required documents
- notes and verification notes

Input now supports optional PAN and optional GSTIN; when provided, the backend
attempts live verification via configured Setu endpoints and logs whether a
live API source or fallback path was used.

### Verification modes (recommended for demos)

Set `VERIFICATION_MODE` to control behavior:

- `mock`: no external calls; returns deterministic mock verification data
- `sandbox`: calls configured sandbox endpoints and labels source as `sandbox_api`
- `live`: calls configured production endpoints and labels source as `live_api`

For resume/demo usage without a business account, use `VERIFICATION_MODE=mock`.

## AI agent orchestration

The API now uses an orchestration layer (`server/agent.py`) with this flow:

1. Parse and validate profile (Pydantic schema)
2. Run deterministic rule engine against verified registration KB
3. Call live verification tools where input is available (GST/PAN via Setu)
4. Optionally run constrained LLM reasoning for summary and action sequencing
   (`AGENT_ENABLE_LLM=true`)
5. Return final `BusinessSetupReport` schema

LLM behavior is constrained to wording/prioritization only and must not
introduce registrations/documents outside tool outputs.

## Action layer (MVP)

The orchestrator now runs an in-memory action layer and returns generated
artifacts in the final response:

- Markdown report (`business_setup_report.md`)
- CSV checklist tracker (`business_setup_tracker.csv`)
- PDF report (`business_setup_report.pdf`, base64 payload)
- Google Sheet append (when configured)
- SMTP email delivery (when configured)

The frontend exposes download buttons for these generated artifacts.

Generated artifacts are also persisted to backend storage and returned as
`artifact_url` links for retrieval.

The backend rule engine (`server/registrations.py`) evaluates the business
profile deterministically against this catalog and returns stable JSON output
for identical inputs.

## Running locally

### Backend

```bash
cd server
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# Requires Ollama running locally with the model pulled:
ollama pull qwen2.5-coder:7b

uvicorn api:app --reload --port 8000
```

Optional live GST verification setup (Setu):

```bash
export SETU_GST_VERIFY_URL="https://api.setu.co/data/gst/{gstin}"
export SETU_BEARER_TOKEN="your_setu_bearer_token"
export SETU_PAN_VERIFY_URL="https://api.setu.co/data/pan/{pan}"
export AGENT_ENABLE_LLM="false"
export OLLAMA_MODEL="qwen2.5-coder:7b"
export VERIFICATION_MODE="sandbox"
export MAX_REQUEST_BYTES="65536"
export GOOGLE_SHEETS_ID="your_google_sheet_id"
export GOOGLE_SHEETS_API_KEY="your_google_api_key"
export GOOGLE_SHEETS_RANGE="Sheet1!A1"
export GOOGLE_SERVICE_ACCOUNT_FILE="/absolute/path/to/service-account.json"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_email"
export SMTP_PASSWORD="your_app_password"
export REPORT_FROM_EMAIL="your_email"
export REPORT_TO_EMAIL="recipient_email"
export RATE_LIMIT_REQUESTS_PER_MINUTE="60"
export CORS_ALLOW_ORIGINS="http://localhost:3000"
export ARTIFACT_BASE_URL="http://127.0.0.1:8000"
export ARTIFACT_BASE_DIR="./artifacts"
```

If these variables are not set, the app still runs and returns deterministic
registration guidance; live verification is marked as not configured/skipped.

### Frontend

```bash
cd client
npm install
npm run dev
```

### Tests

Frontend tests:

```bash
cd client
npm test
```

Backend tests:

```bash
cd server
source env/bin/activate
pytest
```

Open [http://localhost:3000](http://localhost:3000). The frontend proxies
`/api/evaluate` requests to the FastAPI backend at `http://127.0.0.1:8000`
(configurable via `PYTHON_BACKEND_URL`).

## Roadmap

- [x] Business profile intake form with validation (business type, industry,
      state, city, employees, turnover, activity, online/offline, GSTIN, PAN)
- [x] Curated, verified knowledge base of registrations/licences
- [x] Deterministic rule engine: profile → Applicable / More Info Required /
      Not Relevant
- [x] Government API integrations (Setu GST/PAN with mock/sandbox/live modes)
- [x] LLM reasoning layer for constrained wording/prioritization
- [x] Action layer: downloadable reports, Google Sheet tracker, email delivery
- [x] Security baseline: configurable CORS, request limits, rate limiting
- [x] Tests: rules, API, actions, verification modes, end-to-end API flow
- [ ] Bonus: multilingual support, voice input, document-readiness checks,
      human-in-the-loop approval

## Quality and evidence

- Architecture notes: `docs/architecture.md`
- Limitations and legal caveats: `docs/limitations.md`
- Manual scenario matrix: `docs/manual-test-matrix.md`
- Demo runbook: `docs/demo-checklist.md`
- Screenshot placeholders: `docs/screenshots/README.md`

## Demo Gallery

> Add/update screenshots in `docs/screenshots/` and this section will render a
> portfolio-ready walkthrough.

### 1) Business Profile Input

![Business Profile Form](docs/screenshots/01-form-input.png)

### 2) Generated Report Overview

![Report Overview](docs/screenshots/02-report-overview.png)

### 3) Registration Details (Status, Docs, Missing Info)

![Registration Details](docs/screenshots/03-registration-details.png)

### 4) Data Source Logs

![Data Sources](docs/screenshots/04-data-sources.png)

### 5) Action Outputs (MD/CSV/PDF)

![Action Outputs](docs/screenshots/05-action-outputs.png)

### 6) Google Sheet Tracker Result

![Google Sheet Result](docs/screenshots/06-google-sheet-result.png)

### 7) Email Delivery Result

![Email Result](docs/screenshots/07-email-result.png)

### 8) API Docs

![API Docs](docs/screenshots/08-api-docs.png)

## Disclaimer

Output is intended as guidance to help entrepreneurs navigate registration
requirements, not as legal or official government advice. Always verify
current rules, fees, and procedures with the relevant official government
source before acting.

The tool may surface `More Info Required` when details are missing or where
state/industry interpretation is uncertain. In such cases, users should verify
with the relevant government department or a qualified professional before filing.
