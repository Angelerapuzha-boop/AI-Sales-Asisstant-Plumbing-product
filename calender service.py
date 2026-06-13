"""Google Calendar service — OAuth 2.0 + event management."""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import settings

TOKEN_FILE = Path(__file__).parent.parent / "google_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]


def _client_config() -> dict:
    return {
        "web": {
            "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
            "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }


def get_auth_url() -> str:
    """Return Google OAuth URL for Calendar access."""
    flow = Flow.from_client_config(
        _client_config(),
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    return auth_url


def exchange_code(code: str) -> Credentials:
    """Exchange auth code for credentials and save to disk."""
    flow = Flow.from_client_config(
        _client_config(),
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    _save_token(creds)
    return creds


def _save_token(creds: Credentials):
    TOKEN_FILE.write_text(creds.to_json())


def _load_creds() -> Optional[Credentials]:
    if not TOKEN_FILE.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)
    return creds


def _service():
    creds = _load_creds()
    if not creds or not creds.valid:
        raise RuntimeError("Google Calendar not authorized. Please connect via /auth/google")
    return build("calendar", "v3", credentials=creds)


def is_authorized() -> bool:
    try:
        creds = _load_creds()
        return creds is not None and creds.valid
    except Exception:
        return False


def create_event(
    title: str,
    description: str,
    start: datetime,
    end: datetime,
    attendees: list[str],
    add_meet: bool = True,
) -> dict:
    """Create a Google Calendar event with optional Meet link."""
    svc = _service()

    body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
        "end":   {"dateTime": end.isoformat(),   "timeZone": "UTC"},
        "attendees": [{"email": e} for e in attendees],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email",  "minutes": 24 * 60},
                {"method": "popup",  "minutes": 60},
                {"method": "popup",  "minutes": 10},
            ],
        },
    }

    if add_meet:
        body["conferenceData"] = {
            "createRequest": {
                "requestId": f"meet-{int(start.timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }

    event = svc.events().insert(
        calendarId="primary",
        body=body,
        conferenceDataVersion=1 if add_meet else 0,
        sendUpdates="all",
    ).execute()

    meet_link = (
        event.get("conferenceData", {})
             .get("entryPoints", [{}])[0]
             .get("uri", "")
    )
    return {"event_id": event["id"], "meet_link": meet_link, "html_link": event.get("htmlLink", "")}


def delete_event(event_id: str):
    svc = _service()
    try:
        svc.events().delete(calendarId="primary", eventId=event_id).execute()
    except HttpError:
        pass


def list_upcoming_events(max_results: int = 20) -> list[dict]:
    svc = _service()
    now = datetime.utcnow().isoformat() + "Z"
    result = (
        svc.events()
           .list(
               calendarId="primary",
               timeMin=now,
               maxResults=max_results,
               singleEvents=True,
               orderBy="startTime",
           )
           .execute()
    )
    return result.get("items", [])
