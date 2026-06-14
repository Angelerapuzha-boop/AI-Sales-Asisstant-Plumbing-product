"""HTTP client that wraps all backend API calls."""
import os
import requests
from typing import Any, Optional

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 30


def _url(path: str) -> str:
    return f"{BACKEND}{path}"


def _handle(resp: requests.Response) -> Any:
    if resp.status_code in (200, 201):
        return resp.json()
    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:
        detail = resp.text
    raise RuntimeError(f"API {resp.status_code}: {detail}")


# ── Companies ─────────────────────────────────────────────────────────────────

def list_companies(search="", status="", min_score=None, limit=200):
    params = {"limit": limit}
    if search:   params["search"] = search
    if status:   params["status"] = status
    if min_score is not None: params["min_score"] = min_score
    return _handle(requests.get(_url("/companies/"), params=params, timeout=TIMEOUT))

def get_company(cid: int):
    return _handle(requests.get(_url(f"/companies/{cid}"), timeout=TIMEOUT))

def create_company(data: dict):
    return _handle(requests.post(_url("/companies/"), json=data, timeout=TIMEOUT))

def update_company(cid: int, data: dict):
    return _handle(requests.put(_url(f"/companies/{cid}"), json=data, timeout=TIMEOUT))

def delete_company(cid: int):
    return _handle(requests.delete(_url(f"/companies/{cid}"), timeout=TIMEOUT))

def rescore_company(cid: int):
    return _handle(requests.post(_url(f"/companies/{cid}/rescore"), timeout=TIMEOUT))

def company_stats():
    return _handle(requests.get(_url("/companies/stats"), timeout=TIMEOUT))

def import_csv(file_bytes: bytes, filename: str):
    return _handle(requests.post(
        _url("/companies/import/csv"),
        files={"file": (filename, file_bytes, "text/csv")},
        timeout=60,
    ))


# ── Calls ─────────────────────────────────────────────────────────────────────

def list_calls(company_id=None, status=None):
    params = {}
    if company_id: params["company_id"] = company_id
    if status:     params["status"] = status
    return _handle(requests.get(_url("/calls/"), params=params, timeout=TIMEOUT))

def initiate_call(data: dict):
    return _handle(requests.post(_url("/calls/"), json=data, timeout=TIMEOUT))

def sync_call(call_id: int):
    return _handle(requests.post(_url(f"/calls/{call_id}/sync"), timeout=TIMEOUT))

def call_stats():
    return _handle(requests.get(_url("/calls/stats"), timeout=TIMEOUT))


# ── Meetings ──────────────────────────────────────────────────────────────────

def list_meetings(company_id=None, status=None):
    params = {}
    if company_id: params["company_id"] = company_id
    if status:     params["status"] = status
    return _handle(requests.get(_url("/calendar/meetings"), params=params, timeout=TIMEOUT))

def create_meeting(data: dict):
    return _handle(requests.post(_url("/calendar/meetings"), json=data, timeout=TIMEOUT))

def update_meeting(mid: int, data: dict):
    return _handle(requests.put(_url(f"/calendar/meetings/{mid}"), json=data, timeout=TIMEOUT))

def delete_meeting(mid: int):
    return _handle(requests.delete(_url(f"/calendar/meetings/{mid}"), timeout=TIMEOUT))

def meeting_stats():
    return _handle(requests.get(_url("/calendar/meetings/stats"), timeout=TIMEOUT))

def calendar_status():
    return _handle(requests.get(_url("/calendar/status"), timeout=TIMEOUT))

def calendar_auth_url():
    return _handle(requests.get(_url("/calendar/auth"), timeout=TIMEOUT))

def upcoming_events():
    return _handle(requests.get(_url("/calendar/upcoming"), timeout=TIMEOUT))


# ── Emails ────────────────────────────────────────────────────────────────────

def list_emails(company_id=None, status=None):
    params = {}
    if company_id: params["company_id"] = company_id
    if status:     params["status"] = status
    return _handle(requests.get(_url("/emails/"), params=params, timeout=TIMEOUT))

def generate_email(data: dict):
    return _handle(requests.post(_url("/emails/generate"), json=data, timeout=TIMEOUT))

def send_email(email_id: int):
    return _handle(requests.post(_url(f"/emails/{email_id}/send"), timeout=TIMEOUT))

def delete_email(email_id: int):
    return _handle(requests.delete(_url(f"/emails/{email_id}"), timeout=TIMEOUT))

def email_stats():
    return _handle(requests.get(_url("/emails/stats"), timeout=TIMEOUT))

def gmail_status():
    return _handle(requests.get(_url("/emails/status"), timeout=TIMEOUT))

def gmail_auth_url():
    return _handle(requests.get(_url("/emails/auth"), timeout=TIMEOUT))


# ── AI ────────────────────────────────────────────────────────────────────────

def ai_chat(message: str, system: str = ""):
    return _handle(requests.post(_url("/ai/chat"), json={"message": message, "system": system}, timeout=TIMEOUT))

def ai_score(data: dict):
    return _handle(requests.post(_url("/ai/score"), json=data, timeout=TIMEOUT))

def ai_call_script(data: dict):
    return _handle(requests.post(_url("/ai/call-script"), json=data, timeout=TIMEOUT))

def ai_draft_email(data: dict):
    return _handle(requests.post(_url("/ai/draft-email"), json=data, timeout=TIMEOUT))


# ── Notifications ─────────────────────────────────────────────────────────────

def list_notifications(limit=50):
    return _handle(requests.get(_url("/notifications/"), params={"limit": limit}, timeout=TIMEOUT))

def notification_stats():
    return _handle(requests.get(_url("/notifications/stats"), timeout=TIMEOUT))

def test_notification(platform="both"):
    return _handle(requests.post(_url("/notifications/test"), params={"platform": platform}, timeout=TIMEOUT))

def send_manual_notification(event_type: str, detail: str, platform: str = "both"):
    return _handle(requests.post(_url("/notifications/send"), json={
        "event_type": event_type, "detail": detail, "platform": platform
    }, timeout=TIMEOUT))


# ── Health ────────────────────────────────────────────────────────────────────

def health():
    try:
        return _handle(requests.get(_url("/health"), timeout=5))
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}
