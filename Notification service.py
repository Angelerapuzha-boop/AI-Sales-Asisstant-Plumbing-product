"""
Notification service — WhatsApp Business API + Instagram Graph API (Meta).

All notification triggers and their emojis:
  company_added     → 🏢 Company Added
  hot_lead          → 🔥 Hot Lead Alert
  email_generated   → 📧 Email Generated
  email_sent        → ✅ Email Sent
  meeting_scheduled → 📅 Meeting Scheduled
  meeting_completed → ✅ Meeting Completed
  call_initiated    → 📞 Call Initiated
  csv_imported      → 📤 Import Completed
  daily_report      → 📊 Daily Report
  reminder_24h      → 🔔 Meeting Reminder (24h)
  reminder_1h       → ⏰ Meeting Reminder (1h)
  reminder_10min    → ⏰ Meeting Reminder (10min)
"""

import httpx
from datetime import datetime
from typing import Literal
from config import settings

Platform = Literal["whatsapp", "instagram", "both"]

EMOJI_MAP = {
    "company_added":     "🏢",
    "hot_lead":          "🔥",
    "email_generated":   "📧",
    "email_sent":        "✅",
    "meeting_scheduled": "📅",
    "meeting_completed": "✅",
    "call_initiated":    "📞",
    "csv_imported":      "📤",
    "daily_report":      "📊",
    "reminder_24h":      "🔔",
    "reminder_1h":       "⏰",
    "reminder_10min":    "⏰",
}

TITLE_MAP = {
    "company_added":     "Company Added",
    "hot_lead":          "Hot Lead Alert",
    "email_generated":   "Email Generated",
    "email_sent":        "Email Sent",
    "meeting_scheduled": "Meeting Scheduled",
    "meeting_completed": "Meeting Completed",
    "call_initiated":    "Call Initiated",
    "csv_imported":      "Import Completed",
    "daily_report":      "Daily Report",
    "reminder_24h":      "Meeting Reminder (24h)",
    "reminder_1h":       "Meeting Reminder (1h)",
    "reminder_10min":    "Meeting Reminder (10min)",
}

META_GRAPH_URL = "https://graph.facebook.com/v18.0"


async def send_whatsapp(message: str) -> dict:
    """Send WhatsApp message via Meta Business API."""
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        return {"status": "skipped", "reason": "WhatsApp not configured"}

    url = f"{META_GRAPH_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.WHATSAPP_RECIPIENT_NUMBER,
        "type": "text",
        "text": {"body": message},
    }
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, headers=headers, json=payload)
        return {"status": "sent" if resp.is_success else "failed", "code": resp.status_code, "body": resp.json()}


async def send_instagram_dm(message: str) -> dict:
    """Send Instagram DM via Meta Graph API."""
    if not settings.INSTAGRAM_ACCESS_TOKEN or not settings.INSTAGRAM_RECIPIENT_ID:
        return {"status": "skipped", "reason": "Instagram not configured"}

    url = f"{META_GRAPH_URL}/me/messages"
    payload = {
        "recipient": {"id": settings.INSTAGRAM_RECIPIENT_ID},
        "message": {"text": message},
        "messaging_type": "MESSAGE_TAG",
        "tag": "ACCOUNT_UPDATE",
    }
    headers = {
        "Authorization": f"Bearer {settings.INSTAGRAM_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, headers=headers, json=payload)
        return {"status": "sent" if resp.is_success else "failed", "code": resp.status_code, "body": resp.json()}


async def notify(
    event_type: str,
    detail: str = "",
    platform: Platform = "both",
) -> dict:
    """
    Send a structured notification to WhatsApp and/or Instagram.

    Args:
        event_type: one of the keys in EMOJI_MAP
        detail:     extra context (company name, lead score, etc.)
        platform:   "whatsapp" | "instagram" | "both"
    """
    emoji = EMOJI_MAP.get(event_type, "🔔")
    title = TITLE_MAP.get(event_type, event_type.replace("_", " ").title())
    now   = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    message = f"{emoji} *{title}*\n{detail}\n_{now}_"

    results = {}

    if platform in ("whatsapp", "both"):
        results["whatsapp"] = await send_whatsapp(message)

    if platform in ("instagram", "both"):
        results["instagram"] = await send_instagram_dm(message)

    return results
