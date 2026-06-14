"""Google Calendar router — OAuth + event CRUD."""
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Meeting, Company, Notification
from services import calendar_service, notification_service

router = APIRouter(prefix="/calendar", tags=["calendar"])


class MeetingCreate(BaseModel):
    company_id: int
    title: str
    description: Optional[str] = ""
    start_time: datetime
    end_time: datetime
    attendees: List[str] = []
    add_meet_link: Optional[bool] = True


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class MeetingOut(BaseModel):
    id: int
    company_id: int
    calendar_event_id: Optional[str]
    title: str
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    attendees: Optional[list]
    meet_link: Optional[str]
    status: str
    reminders_sent: Optional[list]
    created_at: datetime

    class Config:
        from_attributes = True


def _log_notification(db: Session, event_type: str, message: str, result: dict):
    statuses = [v.get("status", "failed") for v in result.values() if isinstance(v, dict)]
    status = "sent" if any(s == "sent" for s in statuses) else "skipped"
    notif = Notification(
        type=event_type, message=message, platform="both",
        status=status, sent_at=datetime.utcnow() if status == "sent" else None,
    )
    db.add(notif)
    db.commit()


# ── OAuth ─────────────────────────────────────────────────────────────────────

@router.get("/auth")
def start_oauth():
    """Return the Google OAuth URL for Calendar."""
    try:
        url = calendar_service.get_auth_url()
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(500, f"OAuth init error: {e}")


@router.get("/auth/callback")
def oauth_callback(code: str, request: Request):
    """Handle Google OAuth callback and save tokens."""
    try:
        calendar_service.exchange_code(code)
        return {"detail": "Google Calendar connected successfully!"}
    except Exception as e:
        raise HTTPException(400, f"OAuth callback error: {e}")


@router.get("/status")
def calendar_status():
    return {"authorized": calendar_service.is_authorized()}


# ── Meetings ─────────────────────────────────────────────────────────────────

@router.get("/meetings", response_model=list[MeetingOut])
def list_meetings(
    company_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Meeting)
    if company_id:
        q = q.filter(Meeting.company_id == company_id)
    if status:
        q = q.filter(Meeting.status == status)
    return q.order_by(Meeting.start_time.asc()).all()


@router.get("/meetings/stats")
def meeting_stats(db: Session = Depends(get_db)):
    total     = db.query(Meeting).count()
    scheduled = db.query(Meeting).filter(Meeting.status == "scheduled").count()
    completed = db.query(Meeting).filter(Meeting.status == "completed").count()
    return {"total": total, "scheduled": scheduled, "completed": completed}


@router.get("/meetings/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    m = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not m:
        raise HTTPException(404, "Meeting not found")
    return m


@router.post("/meetings", response_model=MeetingOut, status_code=201)
async def create_meeting(payload: MeetingCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == payload.company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")

    calendar_event_id = ""
    meet_link = ""

    if calendar_service.is_authorized():
        try:
            cal_result = calendar_service.create_event(
                title=payload.title,
                description=payload.description or "",
                start=payload.start_time,
                end=payload.end_time,
                attendees=payload.attendees,
                add_meet=payload.add_meet_link,
            )
            calendar_event_id = cal_result.get("event_id", "")
            meet_link = cal_result.get("meet_link", "")
        except Exception as e:
            # Don't block — save locally even if Calendar fails
            meet_link = ""
            calendar_event_id = f"local_{int(datetime.utcnow().timestamp())}"

    meeting = Meeting(
        company_id=payload.company_id,
        calendar_event_id=calendar_event_id,
        title=payload.title,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
        attendees=payload.attendees,
        meet_link=meet_link,
        status="scheduled",
        reminders_sent=[],
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    # Notify
    time_str = payload.start_time.strftime("%d %b %Y, %H:%M UTC")
    detail = (
        f"Meeting scheduled with *{company.name}*\n"
        f"📌 {payload.title}\n"
        f"🕐 {time_str}"
    )
    if meet_link:
        detail += f"\n🔗 {meet_link}"
    result = await notification_service.notify("meeting_scheduled", detail)
    _log_notification(db, "meeting_scheduled", detail, result)

    return meeting


@router.put("/meetings/{meeting_id}", response_model=MeetingOut)
def update_meeting(meeting_id: int, payload: MeetingUpdate, db: Session = Depends(get_db)):
    m = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not m:
        raise HTTPException(404, "Meeting not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(m, field, value)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/meetings/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    m = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not m:
        raise HTTPException(404, "Meeting not found")
    if m.calendar_event_id and not m.calendar_event_id.startswith("local_"):
        try:
            calendar_service.delete_event(m.calendar_event_id)
        except Exception:
            pass
    db.delete(m)
    db.commit()
    return {"detail": "Meeting deleted"}


@router.get("/upcoming")
def upcoming_events():
    """Return upcoming events from Google Calendar."""
    if not calendar_service.is_authorized():
        return {"events": [], "detail": "Not connected to Google Calendar"}
    try:
        events = calendar_service.list_upcoming_events()
        return {"events": events}
    except Exception as e:
        raise HTTPException(500, f"Calendar error: {e}")
