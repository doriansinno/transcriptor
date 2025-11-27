"""Kommunikation mit dem Node.js-Server, der OpenAI ansteuert."""
from __future__ import annotations

import json
from typing import Any, Dict

import requests

BASE_URL = "https://codexgpt-dh73.onrender.com"
IMPROVE_ENDPOINT = f"{BASE_URL}/api/improve-notes"  # Platzhalter
EMERGENCY_ENDPOINT = f"{BASE_URL}/api/emergency-help"  # Platzhalter


class ApiError(Exception):
    """Fehler bei der Kommunikation mit der API."""


def _post_json(url: str, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as exc:  # pragma: no cover - Netzabhängig
        raise ApiError(f"Netzwerkfehler: {exc}") from exc

    if response.status_code != 200:
        raise ApiError(f"Server antwortete mit Status {response.status_code}.")

    try:
        return response.json()
    except json.JSONDecodeError as exc:  # pragma: no cover - Serverabhängig
        raise ApiError("Antwort war kein gültiges JSON.") from exc


def improve_notes(full_text: str, *, license_key: str, timeout: int = 60) -> str:
    payload = {"license_key": license_key, "text": full_text}
    data = _post_json(IMPROVE_ENDPOINT, payload, timeout=timeout)
    improved = data.get("improved_text") or data.get("text") or data
    if isinstance(improved, dict):
        raise ApiError("API lieferte kein Textfeld zurück.")
    return str(improved)


def emergency_help(context_text: str, *, license_key: str, timeout: int = 60) -> Dict[str, Any]:
    payload = {"license_key": license_key, "text": context_text}
    data = _post_json(EMERGENCY_ENDPOINT, payload, timeout=timeout)
    if not isinstance(data, dict):
        raise ApiError("Ungültige Antwort vom Server.")
    return data
