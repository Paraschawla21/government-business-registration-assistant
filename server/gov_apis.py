import json
import os
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
        }

    url = base_url.replace("{gstin}", gstin)
    if "{gstin}" not in base_url:
        url = f"{base_url.rstrip('/')}/{gstin}"

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
        trade_name = _extract_nested_value(data, {"tradename", "trade_name", "tradeName", "tnm".lower()})
        status = _extract_nested_value(data, {"status", "sts", "gststatus"})

        return {
            "checked": True,
            "provider": "setu",
            "gstin": gstin,
            "legal_name": legal_name,
            "trade_name": trade_name,
            "status": status,
            "message": "GSTIN verification completed via Setu.",
            "raw": data,
        }
    except error.HTTPError as exc:
        return {
            "checked": False,
            "provider": "setu",
            "gstin": gstin,
            "message": f"Setu GST verification failed with HTTP {exc.code}.",
        }
    except Exception:
        return {
            "checked": False,
            "provider": "setu",
            "gstin": gstin,
            "message": "Setu GST verification could not be completed.",
        }
