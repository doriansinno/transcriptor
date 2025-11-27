"""Kommunikation mit dem externen Lizenzserver."""
from __future__ import annotations

import json
from typing import Any, Dict

import requests

BASE_URL = "https://codexgpt-dh73.onrender.com"
LICENSE_ENDPOINT = f"{BASE_URL}/license/check"  # Platzhalter


class LicenseError(Exception):
    """Fehler bei der Lizenzprüfung."""


def check_license(key: str, timeout: int = 10) -> Dict[str, Any]:
    if not key:
        raise LicenseError("Kein Lizenzschlüssel angegeben.")

    payload = {"key": key}
    try:
        response = requests.post(LICENSE_ENDPOINT, json=payload, timeout=timeout)
    except requests.RequestException as exc:  # pragma: no cover - Netzabhängig
        raise LicenseError(f"Netzwerkfehler bei der Lizenzprüfung: {exc}") from exc

    if response.status_code != 200:
        raise LicenseError(f"Lizenzserver antwortete mit Status {response.status_code}.")

    try:
        data = response.json()
    except json.JSONDecodeError as exc:  # pragma: no cover - Serverabhängig
        raise LicenseError("Lizenzserver lieferte keine gültige JSON-Antwort.") from exc

    if not data.get("valid", False):
        message = data.get("message", "Lizenz ist ungültig oder abgelaufen.")
        raise LicenseError(message)

    return {
        "valid": True,
        "expires": data.get("expires"),
        "plan": data.get("plan"),
        "message": data.get("message", "OK"),
    }
