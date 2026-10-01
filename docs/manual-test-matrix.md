# Manual Test Matrix

Use this matrix for acceptance checks. Each case should produce explainable
statuses, official links, and no invented registration names/documents.

## Scenarios

1. IT services startup (online, low employees)
- Input: IT, Maharashtra, online, employees=5, turnover=20-40L
- Expected: GST `More Info Required`/`Applicable` (based on turnover + ops), EPFO/ESIC likely not applicable by threshold, FSSAI not relevant.

2. Food outlet (offline, city operations)
- Input: Food & Beverage, offline, employees=12, turnover=40L-1Cr
- Expected: FSSAI applicable, Shops & Establishments likely applicable, GST likely applicable.

3. Manufacturing MSME
- Input: Manufacturing, both, employees=25, turnover=>1Cr
- Expected: EPFO/ESIC applicable, Udyam more-info-required unless investment data supplied.

4. Professional services in Maharashtra
- Input: Professional Services, state=Maharashtra
- Expected: Professional Tax likely applicable with state verification note.

5. Professional services in non-covered state
- Input: Professional Services, state=Rajasthan
- Expected: Professional Tax `More Info Required` with state-specific verification note.

6. International trade intent
- Input activity contains "import/export"
- Expected: IEC applicable.

7. GSTIN provided, verification mode mock
- Env: VERIFICATION_MODE=mock
- Expected: GST verification checked=true, source_type=mock_api.

8. PAN provided, sandbox without credentials
- Env: VERIFICATION_MODE=sandbox, no SETU creds
- Expected: PAN verification checked=false, source_type=not_configured/fallback.

9. Rate limit behavior
- Send > RATE_LIMIT_REQUESTS_PER_MINUTE within 60 seconds from same IP
- Expected: HTTP 429.

10. Oversized payload behavior
- Input activity > MAX_REQUEST_BYTES threshold effective body size
- Expected: HTTP 413.
