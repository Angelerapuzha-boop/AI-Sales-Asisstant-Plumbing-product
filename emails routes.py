"""Email router — Groq generation + Gmail sending + OAuth."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Email, Company, Notification
from services import groq_service, gmail_service, notification_service

router = APIRouter(prefix="/emails", tags=["emails"])


class EmailGenerate(BaseModel):
    company_id: int
    sender_name: Optional[str] = "Sales Team"
    extra_context: Optional[str] = ""


class EmailSend(BaseModel):
    email_id: int


class EmailOut(BaseModel):
    id: int
    company_id: int
    subject: Optional[str]
    body: Optional[str]
    recipient_email: Optional[str]
    gmail_message_id: Optional[str]
    status: str
    created_at: datetime
    sent_at: Optional[datetime]

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
def start_gmail_oauth():
    try:
        url = gmail_service.get_auth_url()
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(500, f"Gmail OAuth error: {e}")


@router.get("/auth/callback_gmail")
def gmail_callback(code: str):
    try:
        gmail_service.exchange_code(code)
        return {"detail": "Gmail connected successfully!"}
    except Exception as e:
        raise HTTPException(400, f"Gmail callback error: {e}")


@router.get("/status")
def gmail_status():
    return {"authorized": gmail_service.is_authorized()}


# ── Email CRUD ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[EmailOut])
def list_emails(
    company_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Email)
    if company_id:
        q = q.filter(Email.company_id == company_id)
    if status:
        q = q.filter(Email.status == status)
    return q.order_by(Email.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/stats")
def email_stats(db: Session = Depends(get_db)):
    total     = db.query(Email).count()
    generated = db.query(Email).filter(Email.status == "generated").count()
    sent      = db.query(Email).filter(Email.status == "sent").count()
    failed    = db.query(Email).filter(Email.status == "failed").count()
    return {"total": total, "generated": generated, "sent": sent, "failed": failed}


@router.get("/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db: Session = Depends(get_db)):
    e = db.query(Email).filter(Email.id == email_id).first()
    if not e:
        raise HTTPException(404, "Email not found")
    return e


@router.post("/generate", response_model=EmailOut, status_code=201)
async def generate_email(payload: EmailGenerate, db: Session = Depends(get_db)):
    """Use Groq Llama-3 to generate a personalised sales email."""
    company = db.query(Company).filter(Company.id == payload.company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")

    notes = "\n".join(filter(None, [company.notes, payload.extra_context]))

    try:
        result = groq_service.generate_sales_email(
            company_name=company.name,
            contact_name=company.contact_name or "Sir/Madam",
            industry=company.industry or "your industry",
            notes=notes,
            sender_name=payload.sender_name or "Sales Team",
        )
    except Exception as e:
        raise HTTPException(502, f"Groq error: {e}")

    email = Email(
        company_id=payload.company_id,
        subject=result.get("subject", ""),
        body=result.get("body", ""),
        recipient_email=company.email or "",
        status="generated",
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    # Notify
    detail = f"Email generated for *{company.name}*\n📌 {email.subject}"
    notif_result = await notification_service.notify("email_generated", detail)
    _log_notification(db, "email_generated", detail, notif_result)

    return email


@router.post("/{email_id}/send")
async def send_email(email_id: int, db: Session = Depends(get_db)):
    """Send the email via Gmail API."""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(404, "Email not found")
    if not email.recipient_email:
        raise HTTPException(400, "No recipient email on file")

    if not gmail_service.is_authorized():
        raise HTTPException(403, "Gmail not connected. Authorize at /emails/auth")

    try:
        sent = gmail_service.send_email(
            to=email.recipient_email,
            subject=email.subject or "",
            body=email.body or "",
        )
        email.status = "sent"
        email.sent_at = datetime.utcnow()
        email.gmail_message_id = sent.get("message_id", "")
    except Exception as e:
        email.status = "failed"
        db.commit()
        raise HTTPException(502, f"Gmail send error: {e}")

    db.commit()
    db.refresh(email)

    company = db.query(Company).filter(Company.id == email.company_id).first()
    company_name = company.name if company else "Unknown"
    detail = f"Email sent to *{email.recipient_email}*\n🏢 {company_name}\n📌 {email.subject}"
    result = await notification_service.notify("email_sent", detail)
    _log_notification(db, "email_sent", detail, result)

    return {"detail": "Email sent", "message_id": email.gmail_message_id}


@router.delete("/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_db)):
    e = db.query(Email).filter(Email.id == email_id).first()
    if not e:
        raise HTTPException(404, "Email not found")
    db.delete(e)
    db.commit()
    return {"detail": "Deleted"}
