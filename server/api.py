import os
import smtplib
import socket
import ssl
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path
from urllib import error, request

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
ARTIFACT_RETENTION_HOURS = int(os.getenv("ARTIFACT_RETENTION_HOURS", "24"))
MAX_ARTIFACT_RUNS = int(os.getenv("MAX_ARTIFACT_RUNS", "200"))

_request_windows: dict[str, deque[float]] = defaultdict(deque)


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}***{value[-2:]}"


def _check_ollama() -> dict:
    llm_enabled = os.getenv("AGENT_ENABLE_LLM", "false").strip().lower() == "true"
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")

    if not llm_enabled:
        return {
            "name": "ollama",
            "status": "skipped",
            "configured": False,
            "reachable": False,
            "message": "LLM orchestration is disabled (AGENT_ENABLE_LLM=false).",
        }

    try:
        import ollama

        client = ollama.Client()
        listed = client.list()
        model_names = [item.get("name", "") for item in listed.get("models", [])]
        has_model = any(name.startswith(model_name) for name in model_names)
        return {
            "name": "ollama",
            "status": "ok" if has_model else "degraded",
            "configured": True,
            "reachable": True,
            "model": model_name,
            "message": (
                f"Ollama reachable. Model {'found' if has_model else 'not found'}: {model_name}."
            ),
        }
    except Exception as exc:
        return {
            "name": "ollama",
            "status": "error",
            "configured": True,
            "reachable": False,
            "model": model_name,
            "message": f"Ollama check failed: {type(exc).__name__}",
        }


def _check_google_sheets() -> dict:
    sheets_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
    range_name = os.getenv("GOOGLE_SHEETS_RANGE", "Sheet1!A1")
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
    api_key = os.getenv("GOOGLE_SHEETS_API_KEY", "").strip()

    if not sheets_id:
        return {
            "name": "google_sheets",
            "status": "skipped",
            "configured": False,
            "reachable": False,
            "message": "GOOGLE_SHEETS_ID is missing.",
        }

    # Preferred: service account
    if service_account_json or service_account_file:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            if service_account_json:
                import json

                creds_info = json.loads(service_account_json)
            else:
                import json

                with open(service_account_file, "r", encoding="utf-8") as fh:
                    creds_info = json.load(fh)

            credentials = service_account.Credentials.from_service_account_info(
                creds_info,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            service = build("sheets", "v4", credentials=credentials)
            service.spreadsheets().get(
                spreadsheetId=sheets_id,
                fields="spreadsheetId",
            ).execute()
            return {
                "name": "google_sheets",
                "status": "ok",
                "configured": True,
                "reachable": True,
                "mode": "service_account",
                "range": range_name,
                "message": "Google Sheets reachable via service account.",
            }
        except Exception as exc:
            return {
                "name": "google_sheets",
                "status": "error",
                "configured": True,
                "reachable": False,
                "mode": "service_account",
                "range": range_name,
                "message": f"Service account check failed: {type(exc).__name__}",
            }

    # Fallback: API key
    if api_key:
        endpoint = (
            f"https://sheets.googleapis.com/v4/spreadsheets/{sheets_id}"
            f"?fields=spreadsheetId&key={api_key}"
        )
        req = request.Request(endpoint, method="GET")
        try:
            with request.urlopen(req, timeout=10) as response:
                if 200 <= response.status < 300:
                    return {
                        "name": "google_sheets",
                        "status": "ok",
                        "configured": True,
                        "reachable": True,
                        "mode": "api_key",
                        "range": range_name,
                        "message": "Google Sheets reachable via API key.",
                    }
        except error.HTTPError as exc:
            return {
                "name": "google_sheets",
                "status": "error",
                "configured": True,
                "reachable": False,
                "mode": "api_key",
                "range": range_name,
                "message": f"API key check failed with HTTP {exc.code}.",
            }
        except Exception as exc:
            return {
                "name": "google_sheets",
                "status": "error",
                "configured": True,
                "reachable": False,
                "mode": "api_key",
                "range": range_name,
                "message": f"API key check failed: {type(exc).__name__}",
            }

    return {
        "name": "google_sheets",
        "status": "skipped",
        "configured": False,
        "reachable": False,
        "message": "No service account or API key configured.",
    }


def _check_smtp() -> dict:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "0") or "0")
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("REPORT_FROM_EMAIL", "").strip()
    recipient = os.getenv("REPORT_TO_EMAIL", "").strip()

    if not all([host, port, username, password, sender, recipient]):
        return {
            "name": "smtp_email",
            "status": "skipped",
            "configured": False,
            "reachable": False,
            "message": "SMTP env vars are incomplete.",
        }

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=12) as server:
            server.ehlo()
            if server.has_extn("starttls"):
                server.starttls(context=context)
                server.ehlo()
            server.login(username, password)
        return {
            "name": "smtp_email",
            "status": "ok",
            "configured": True,
            "reachable": True,
            "host": host,
            "port": port,
            "username": _mask_secret(username),
            "message": "SMTP connectivity and login succeeded.",
        }
    except (smtplib.SMTPException, socket.error) as exc:
        return {
            "name": "smtp_email",
            "status": "error",
            "configured": True,
            "reachable": False,
            "host": host,
            "port": port,
            "username": _mask_secret(username),
            "message": f"SMTP check failed: {type(exc).__name__}",
        }


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

    _cleanup_artifacts()
    return report


def _cleanup_artifacts() -> None:
    now = time.time()
    retention_seconds = ARTIFACT_RETENTION_HOURS * 3600

    run_dirs = [path for path in ARTIFACT_DIR.iterdir() if path.is_dir()]

    # Remove old runs beyond retention window.
    for run_dir in run_dirs:
        try:
            if now - run_dir.stat().st_mtime > retention_seconds:
                for child in run_dir.iterdir():
                    child.unlink(missing_ok=True)
                run_dir.rmdir()
        except Exception:
            continue

    # Cap number of retained runs.
    run_dirs = [path for path in ARTIFACT_DIR.iterdir() if path.is_dir()]
    if len(run_dirs) <= MAX_ARTIFACT_RUNS:
        return

    run_dirs.sort(key=lambda p: p.stat().st_mtime)
    overflow = len(run_dirs) - MAX_ARTIFACT_RUNS
    for run_dir in run_dirs[:overflow]:
        try:
            for child in run_dir.iterdir():
                child.unlink(missing_ok=True)
            run_dir.rmdir()
        except Exception:
            continue


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


@app.get("/api/health/integrations")
async def integration_health():
    checks = [_check_ollama(), _check_google_sheets(), _check_smtp()]
    overall = "ok" if all(item.get("status") in {"ok", "skipped"} for item in checks) else "degraded"
    return {
        "status": overall,
        "checks": checks,
    }
