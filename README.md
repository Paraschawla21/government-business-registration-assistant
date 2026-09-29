# Government Business Registration Assistant

An AI Agent workflow that helps first-time entrepreneurs in India understand which
government registrations, licences, and approvals may apply to their business —
based on business type, industry, location, employee count, turnover, and
activity — and generates an actionable, step-by-step setup checklist.

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
- **Planned:** Government data sources / APIs (e.g. APISetu, GST verification),
  a deterministic rule-engine knowledge base, and an action layer (PDF/Markdown
  report, Google Sheet tracker, email notifications)

## Repo structure

```
client/   Next.js frontend — business profile intake form + results view
server/   FastAPI backend — Ollama-backed evaluation endpoint
```

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

### Frontend

```bash
cd client
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The frontend proxies
`/api/evaluate` requests to the FastAPI backend at `http://127.0.0.1:8000`
(configurable via `PYTHON_BACKEND_URL`).

## Roadmap

- [x] Business profile intake form with validation (business type, industry,
      state, city, employees, turnover, activity, online/offline, GSTIN)
- [x] FastAPI backend with Ollama structured/schema-validated output
- [ ] Curated, verified knowledge base of registrations/licences (GST, Udyam,
      Shop & Establishment, Professional Tax, FSSAI, EPFO, ESIC, etc.)
- [ ] Deterministic rule engine: profile → Applicable / More Info Required /
      Not Relevant, per registration
- [ ] Government API integrations (e.g. APISetu, GST verification)
- [ ] LLM reasoning layer: explain relevance, sequence steps, phrase
      follow-up questions — constrained to only the data provided
- [ ] Action layer: downloadable report, Google Sheet tracker, email delivery
- [ ] Bonus: multilingual support, voice input, document-readiness checks,
      human-in-the-loop approval

## Disclaimer

Output is intended as guidance to help entrepreneurs navigate registration
requirements, not as legal or official government advice. Always verify
current rules, fees, and procedures with the relevant official government
source before acting.

The tool may surface `More Info Required` when details are missing or where
state/industry interpretation is uncertain. In such cases, users should verify
with the relevant government department or a qualified professional before filing.
