import json
import os
import time
from typing import Any, Optional
from urllib import error, request


def _extract_nested_value(payload: Any, keys: set[str]) -> Optional[str]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key.lower() in keys and value not in (None, ""):
                return str(value)
            nested = _extract_nested_value(value, keys)
            if nested:
                return nested
    if isinstance(payload, list):
        for item in payload:
            nested = _extract_nested_value(item, keys)
            if nested:
                return nested
    return None


def verify_gstin_with_setu(gstin: str) -> dict[str, Any]:
    """
    Optional live GST verification via Setu.

    Required env vars:
    - SETU_GST_VERIFY_URL
      e.g. https://api.setu.co/data/gst/{gstin}
    - SETU_BEARER_TOKEN
    """

    base_url = os.getenv("SETU_GST_VERIFY_URL", "").strip()
    token = os.getenv("SETU_BEARER_TOKEN", "").strip()

    if not base_url or not token:
        return {
            "checked": False,
            "provider": "setu",
            "message": "Setu GST verification is not configured.",
            "source_type": "not_configured",
        }

    url = base_url.replace("{gstin}", gstin)
    if "{gstin}" not in base_url:
        url = f"{base_url.rstrip('/')}/{gstin}"

    attempts = 2
    backoff_seconds = 1

    for attempt in range(1, attempts + 1):
        req = request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="GET",
        )

        try:
            with request.urlopen(req, timeout=12) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body) if body else {}

            legal_name = _extract_nested_value(data, {"legalname", "lgnm", "name"})
            trade_name = _extract_nested_value(
                data, {"tradename", "trade_name", "tradename", "tnm"}
            )
            status = _extract_nested_value(data, {"status", "sts", "gststatus"})

            return {
                "checked": True,
                "provider": "setu",
                "gstin": gstin,
                "legal_name": legal_name,
                "trade_name": trade_name,
                "status": status,
                "message": "GSTIN verification completed via Setu.",
                "source_type": "live_api",
                "raw": data,
            }
        except error.HTTPError as exc:
            if attempt < attempts and exc.code >= 500:
                time.sleep(backoff_seconds)
                continue
            return {
                "checked": False,
                "provider": "setu",
                "gstin": gstin,
                "message": f"Setu GST verification failed with HTTP {exc.code}.",
                "source_type": "live_api",
            }
        except Exception:
            if attempt < attempts:
                time.sleep(backoff_seconds)
                continue
            return {
                "checked": False,
                "provider": "setu",
                "gstin": gstin,
                "message": "Setu GST verification could not be completed.",
                "source_type": "live_api",
            }

    return {
        "checked": False,
        "provider": "setu",
        "gstin": gstin,
        "message": "Setu GST verification timed out after retries.",
        "source_type": "live_api",
    }


def verify_pan_with_setu(pan: str) -> dict[str, Any]:
    """
    Optional live PAN verification via Setu.

    Required env vars:
    - SETU_PAN_VERIFY_URL
      e.g. https://api.setu.co/data/pan/{pan}
    - SETU_BEARER_TOKEN
    """

    base_url = os.getenv("SETU_PAN_VERIFY_URL", "").strip()
    token = os.getenv("SETU_BEARER_TOKEN", "").strip()

    if not base_url or not token:
        return {
            "checked": False,
            "provider": "setu",
            "message": "Setu PAN verification is not configured.",
            "source_type": "not_configured",
        }

    url = base_url.replace("{pan}", pan.upper())
    if "{pan}" not in base_url:
        url = f"{base_url.rstrip('/')}/{pan.upper()}"

    attempts = 2
    backoff_seconds = 1
    for attempt in range(1, attempts + 1):
        req = request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="GET",
        )
        try:
            with request.urlopen(req, timeout=12) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body) if body else {}

            holder_name = _extract_nested_value(data, {"name", "full_name", "holdername"})
            status = _extract_nested_value(data, {"status", "panstatus", "result"})

            return {
                "checked": True,
                "provider": "setu",
                "pan": pan.upper(),
                "name": holder_name,
                "status": status,
                "message": "PAN verification completed via Setu.",
                "source_type": "live_api",
                "raw": data,
            }
        except error.HTTPError as exc:
            if attempt < attempts and exc.code >= 500:
                time.sleep(backoff_seconds)
                continue
            return {
                "checked": False,
                "provider": "setu",
                "pan": pan.upper(),
                "message": f"Setu PAN verification failed with HTTP {exc.code}.",
                "source_type": "live_api",
            }
        except Exception:
            if attempt < attempts:
                time.sleep(backoff_seconds)
                continue
            return {
                "checked": False,
                "provider": "setu",
                "pan": pan.upper(),
                "message": "Setu PAN verification could not be completed.",
                "source_type": "live_api",
            }

    return {
        "checked": False,
        "provider": "setu",
        "pan": pan.upper(),
        "message": "Setu PAN verification timed out after retries.",
        "source_type": "live_api",
    }
