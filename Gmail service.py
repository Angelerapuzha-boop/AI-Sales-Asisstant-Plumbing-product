"""Gmail service — OAuth 2.0 + email sending via Gmail API."""
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from config import settings

TOKEN_FILE = Path(__file__).parent.parent / "gmail_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]


def _client_config() -> dict:
    return {
        "web": {
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI + "_gmail"],
        }
    }


def get_auth_url() -> str:
    flow = Flow.from_client_config(
        _client_config(),
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI + "_gmail",
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    return auth_url


def exchange_code(code: str) -> Credentials:
    flow = Flow.from_client_config(
        _client_config(),
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI + "_gmail",
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
        raise RuntimeError("Gmail not authorized. Please connect via /auth/gmail")
    return build("gmail", "v1", credentials=creds)


def is_authorized() -> bool:
    try:
        creds = _load_creds()
        return creds is not None and creds.valid
    except Exception:
        return False


def _build_message(to: str, subject: str, body: str, html: bool = False) -> dict:
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.GMAIL_SENDER_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    part = MIMEText(body, "html" if html else "plain")
    msg.attach(part)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_email(to: str, subject: str, body: str, html: bool = False) -> dict:
    """Send an email via Gmail API. Returns message info dict."""
    svc = _service()
    message = _build_message(to, subject, body, html)
    sent = svc.users().messages().send(userId="me", body=message).execute()
    return {"message_id": sent.get("id", ""), "thread_id": sent.get("threadId", "")}


def list_sent(max_results: int = 20) -> list[dict]:
    svc = _service()
    result = (
        svc.users()
           .messages()
           .list(userId="me", labelIds=["SENT"], maxResults=max_results)
           .execute()
    )
    return result.get("messages", [])
