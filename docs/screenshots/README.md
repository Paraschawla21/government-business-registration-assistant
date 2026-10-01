# Screenshots Placeholder

Add curated screenshots here for README and resume evidence.

Recommended file names:

- `01-form-input.png` - business profile form before submission
- `02-report-overview.png` - generated registration report summary
- `03-registration-details.png` - status, docs, missing info, official links
- `04-data-sources.png` - data source logs (KB + verification mode)
- `05-action-outputs.png` - markdown/csv/pdf download actions
- `06-google-sheet-result.png` - sheet tracker append result (if configured)
- `07-email-result.png` - email delivery status (if configured)
- `08-api-docs.png` - FastAPI docs endpoint view

Tip:
- Keep screenshots at consistent resolution.
- Blur any sensitive identifiers before committing.

## Capture guide (quick)

1. Run app locally and keep browser zoom at 100%.
2. Use the same browser window size for all captures.
3. Capture full-page where possible for consistency.
4. Save using the exact file names above.
5. Re-run README and ensure image links render on GitHub.

## Recommended command snippets for capture session

Backend:

```bash
cd server
source env/bin/activate
set -a && source .env && set +a
uvicorn api:app --reload --port 8000
```

Frontend:

```bash
cd client
npm run dev
```

Optional (mock mode for deterministic screenshots):

```env
VERIFICATION_MODE=mock
AGENT_ENABLE_LLM=false
```
