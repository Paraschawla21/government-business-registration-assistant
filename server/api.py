import os
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from agent import run_business_setup_agent
from schemas import BusinessProfile, BusinessSetupReport

app = FastAPI(title="AI Tool Evaluator API")

MAX_CONTENT_LENGTH = int(os.getenv("MAX_REQUEST_BYTES", "65536"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
ARTIFACT_BASE_URL = os.getenv("ARTIFACT_BASE_URL", "http://127.0.0.1:8000")

_request_windows: dict[str, deque[float]] = defaultdict(deque)


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


ARTIFACT_DIR = Path(
    os.getenv("ARTIFACT_BASE_DIR", str(Path(__file__).resolve().parent / "artifacts"))
)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

app.mount("/artifacts", StaticFiles(directory=str(ARTIFACT_DIR)), name="artifacts")


@app.middleware("http")
async def request_context_and_rate_limit(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _request_windows[client_ip]

    while window and now - window[0] > 60:
        window.popleft()

    if len(window) >= RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please retry shortly."},
            headers={"X-Request-ID": request_id},
        )

    window.append(now)
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def _persist_artifacts(report: BusinessSetupReport) -> BusinessSetupReport:
    run_id = str(uuid.uuid4())
    run_dir = ARTIFACT_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    for result in report.action_results:
        if result.artifact_content and result.artifact_filename:
            file_path = run_dir / result.artifact_filename
            file_path.write_text(result.artifact_content, encoding="utf-8")
            result.artifact_url = f"{ARTIFACT_BASE_URL}/artifacts/{run_id}/{result.artifact_filename}"

        if result.artifact_base64 and result.artifact_filename:
            import base64

            file_path = run_dir / result.artifact_filename
            file_path.write_bytes(base64.b64decode(result.artifact_base64))
            result.artifact_url = f"{ARTIFACT_BASE_URL}/artifacts/{run_id}/{result.artifact_filename}"

    return report


@app.post("/api/evaluate", response_model=BusinessSetupReport)
async def evaluate_business_profile(payload: BusinessProfile):
    try:
        if len(payload.model_dump_json().encode("utf-8")) > MAX_CONTENT_LENGTH:
            raise HTTPException(status_code=413, detail="Request payload too large.")
        report = run_business_setup_agent(payload)
        return _persist_artifacts(report)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
