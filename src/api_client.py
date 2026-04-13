from __future__ import annotations

from typing import Any, Dict, List

import requests


class ApiClientError(Exception):
    pass


def _format_detail(detail: Any) -> str:
    if isinstance(detail, list):
        messages = []
        for item in detail:
            if isinstance(item, dict):
                field = " → ".join(str(part) for part in item.get("loc", []) if part != "body")
                msg = item.get("msg", "Invalid input")
                messages.append(f"{field}: {msg}" if field else msg)
            else:
                messages.append(str(item))
        return "\n".join(messages)
    if isinstance(detail, dict):
        return str(detail.get("msg") or detail.get("detail") or detail)
    return str(detail)


def _handle_response(response: requests.Response) -> Any:
    try:
        payload = response.json()
    except Exception:
        payload = response.text

    if not response.ok:
        if isinstance(payload, dict):
            detail = payload.get("detail", payload)
        else:
            detail = payload
        raise ApiClientError(_format_detail(detail))
    return payload


def health_check(base_url: str) -> Dict[str, Any]:
    response = requests.get(f"{base_url.rstrip('/')}/api/health", timeout=10)
    return _handle_response(response)


def register_user(base_url: str, username: str, email: str, password: str, preferred_language: str = "en") -> Dict[str, Any]:
    response = requests.post(
        f"{base_url.rstrip('/')}/api/auth/register",
        json={"username": username, "email": email, "password": password, "preferred_language": preferred_language},
        timeout=15,
    )
    return _handle_response(response)


def login_user(base_url: str, email: str, password: str) -> Dict[str, Any]:
    response = requests.post(
        f"{base_url.rstrip('/')}/api/auth/login",
        json={"email": email, "password": password},
        timeout=15,
    )
    return _handle_response(response)


def get_current_user(base_url: str, token: str) -> Dict[str, Any]:
    response = requests.get(
        f"{base_url.rstrip('/')}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    return _handle_response(response)


def update_language_preference(base_url: str, token: str, preferred_language: str) -> Dict[str, Any]:
    response = requests.put(
        f"{base_url.rstrip('/')}/api/auth/preferences/language",
        json={"preferred_language": preferred_language},
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    return _handle_response(response)


def predict(base_url: str, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(
        f"{base_url.rstrip('/')}/api/predict",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    return _handle_response(response)


def get_history(base_url: str, token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{base_url.rstrip('/')}/api/history/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    payload = _handle_response(response)
    return payload if isinstance(payload, list) else []


def get_admin_stats(base_url: str, token: str) -> Dict[str, Any]:
    response = requests.get(
        f"{base_url.rstrip('/')}/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    return _handle_response(response)


def get_admin_users(base_url: str, token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{base_url.rstrip('/')}/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    payload = _handle_response(response)
    return payload if isinstance(payload, list) else []


def get_admin_predictions(base_url: str, token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{base_url.rstrip('/')}/api/admin/predictions",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    payload = _handle_response(response)
    return payload if isinstance(payload, list) else []
