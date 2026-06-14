"""Notifications router — history + manual trigger + test."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Notification
from services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


class ManualNotify(BaseModel):
    event_type: str
    detail: str
    platform: Optional[str] = "both"


class NotificationOut(BaseModel):
    id: int
    type: str
    message: Optional[str]
    platform: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/", response_model=list[NotificationOut])
def list_notifications(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(Notification)
    if platform:
        q = q.filter(Notification.platform == platform)
    if status:
        q = q.filter(Notification.status == status)
    return q.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/stats")
def notification_stats(db: Session = Depends(get_db)):
    total  = db.query(Notification).count()
    sent   = db.query(Notification).filter(Notification.status == "sent").count()
    failed = db.query(Notification).filter(Notification.status == "failed").count()
    skip   = db.query(Notification).filter(Notification.status == "skipped").count()
    return {"total": total, "sent": sent, "failed": failed, "skipped": skip}


@router.post("/test")
async def test_notification(platform: str = "both"):
    """Send a test notification to verify the integration."""
    result = await notification_service.notify(
        "company_added",
        "🧪 Test notification from ProPlumb AI Sales CRM — all systems operational!",
        platform=platform,  # type: ignore
    )
    return {"result": result}


@router.post("/send")
async def manual_notify(payload: ManualNotify, db: Session = Depends(get_db)):
    result = await notification_service.notify(
        payload.event_type,
        payload.detail,
        platform=payload.platform or "both",  # type: ignore
    )
    statuses = [v.get("status", "failed") for v in result.values() if isinstance(v, dict)]
    status = "sent" if any(s == "sent" for s in statuses) else "skipped"
    notif = Notification(
        type=payload.event_type,
        message=payload.detail,
        platform=payload.platform or "both",
        status=status,
        sent_at=datetime.utcnow() if status == "sent" else None,
    )
    db.add(notif)
    db.commit()
    return {"result": result, "status": status}


@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(404, "Notification not found")
    db.delete(n)
    db.commit()
    return {"detail": "Deleted"}
