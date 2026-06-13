"""
Background scheduler:
  • Daily report at 18:00 UTC
  • Meeting reminders at 24h, 1h, 10min before start
"""

import asyncio
import logging
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Meeting, Company, Email, Call, Notification
from services import notification_service, groq_service

log = logging.getLogger("scheduler")
UTC = pytz.utc

scheduler = AsyncIOScheduler(timezone=UTC)


# ── helpers ──────────────────────────────────────────────────────────────────

def _db() -> Session:
    return SessionLocal()


async def _log_notification(db: Session, event_type: str, message: str, result: dict):
    platform = "both"
    statuses = [v.get("status", "failed") for v in result.values() if isinstance(v, dict)]
    status = "sent" if any(s == "sent" for s in statuses) else "failed"
    notif = Notification(
        type=event_type,
        message=message,
        platform=platform,
        status=status,
        sent_at=datetime.utcnow() if status == "sent" else None,
    )
    db.add(notif)
    db.commit()


# ── MEETING REMINDERS ────────────────────────────────────────────────────────

async def check_meeting_reminders():
    """Run every minute, check for meetings needing 24h / 1h / 10min reminders."""
    db = _db()
    try:
        now = datetime.utcnow()
        meetings = db.query(Meeting).filter(Meeting.status == "scheduled").all()

        for meeting in meetings:
            if not meeting.start_time:
                continue

            reminders_sent: list = meeting.reminders_sent or []
            delta = meeting.start_time - now
            minutes_left = delta.total_seconds() / 60
            company = db.query(Company).filter(Company.id == meeting.company_id).first()
            company_name = company.name if company else "Unknown"

            # Mark as completed if past
            if minutes_left < 0:
                meeting.status = "completed"
                db.commit()
                result = await notification_service.notify(
                    "meeting_completed",
                    f"Meeting with {company_name} — {meeting.title}",
                )
                await _log_notification(db, "meeting_completed", meeting.title, result)
                continue

            # 24-hour reminder
            if 1440 >= minutes_left > 1380 and "24h" not in reminders_sent:
                detail = f"Meeting with *{company_name}* in ~24 hours\n📌 {meeting.title}\n🕐 {meeting.start_time.strftime('%Y-%m-%d %H:%M UTC')}"
                result = await notification_service.notify("reminder_24h", detail)
                await _log_notification(db, "reminder_24h", detail, result)
                reminders_sent.append("24h")
                meeting.reminders_sent = reminders_sent
                db.commit()
                log.info("Sent 24h reminder for meeting %s", meeting.id)

            # 1-hour reminder
            elif 60 >= minutes_left > 50 and "1h" not in reminders_sent:
                detail = f"Meeting with *{company_name}* in 1 hour!\n📌 {meeting.title}"
                if meeting.meet_link:
                    detail += f"\n🔗 {meeting.meet_link}"
                result = await notification_service.notify("reminder_1h", detail)
                await _log_notification(db, "reminder_1h", detail, result)
                reminders_sent.append("1h")
                meeting.reminders_sent = reminders_sent
                db.commit()
                log.info("Sent 1h reminder for meeting %s", meeting.id)

            # 10-minute reminder
            elif 10 >= minutes_left > 7 and "10min" not in reminders_sent:
                detail = f"⚠️ Meeting with *{company_name}* in 10 minutes!\n📌 {meeting.title}"
                if meeting.meet_link:
                    detail += f"\n🔗 {meeting.meet_link}"
                result = await notification_service.notify("reminder_10min", detail)
                await _log_notification(db, "reminder_10min", detail, result)
                reminders_sent.append("10min")
                meeting.reminders_sent = reminders_sent
                db.commit()
                log.info("Sent 10min reminder for meeting %s", meeting.id)

    except Exception as e:
        log.error("Reminder check error: %s", e)
    finally:
        db.close()


# ── DAILY REPORT ─────────────────────────────────────────────────────────────

async def send_daily_report():
    """Send a daily report at 18:00 UTC every day."""
    db = _db()
    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        new_companies   = db.query(Company).filter(Company.created_at >= today_start).count()
        hot_leads       = db.query(Company).filter(Company.lead_score >= 80).count()
        calls_today     = db.query(Call).filter(Call.created_at >= today_start).count()
        emails_sent     = db.query(Email).filter(Email.sent_at >= today_start, Email.status == "sent").count()
        meetings_sched  = db.query(Meeting).filter(Meeting.created_at >= today_start).count()
        total_companies = db.query(Company).count()

        stats = {
            "date": today_start.strftime("%Y-%m-%d"),
            "new_companies_today": new_companies,
            "total_companies": total_companies,
            "hot_leads (score≥80)": hot_leads,
            "calls_made_today": calls_today,
            "emails_sent_today": emails_sent,
            "meetings_scheduled_today": meetings_sched,
        }

        summary = groq_service.generate_daily_report(stats)
        detail  = f"*{today_start.strftime('%A, %d %b %Y')}*\n\n{summary}"

        result = await notification_service.notify("daily_report", detail)
        await _log_notification(db, "daily_report", detail, result)
        log.info("Daily report sent: %s", result)

    except Exception as e:
        log.error("Daily report error: %s", e)
    finally:
        db.close()


# ── SCHEDULER SETUP ──────────────────────────────────────────────────────────

def start():
    scheduler.add_job(
        check_meeting_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="meeting_reminders",
        replace_existing=True,
        misfire_grace_time=30,
    )
    scheduler.add_job(
        send_daily_report,
        trigger=CronTrigger(hour=18, minute=0, timezone=UTC),
        id="daily_report",
        replace_existing=True,
        misfire_grace_time=300,
    )
    scheduler.start()
    log.info("Scheduler started — reminders every 1 min, daily report at 18:00 UTC")


def stop():
    if scheduler.running:
        scheduler.shutdown(wait=False)
