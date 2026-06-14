"""AI Calls router — Bland AI phone call management."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Call, Company, Notification
from services import bland_service, groq_service, notification_service

router = APIRouter(prefix="/calls", tags=["calls"])


class CallCreate(BaseModel):
    company_id: int
    phone_number: str
    custom_task: Optional[str] = None
    voice: Optional[str] = "maya"
    max_duration: Optional[int] = 12


class CallOut(BaseModel):
    id: int
    company_id: int
    bland_call_id: Optional[str]
    phone_number: Optional[str]
    status: str
    duration: Optional[int]
    transcript: Optional[str]
    recording_url: Optional[str]
    summary: Optional[str]
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


@router.get("/", response_model=list[CallOut])
def list_calls(
    company_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Call)
    if company_id:
        q = q.filter(Call.company_id == company_id)
    if status:
        q = q.filter(Call.status == status)
    return q.order_by(Call.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/stats")
def call_stats(db: Session = Depends(get_db)):
    total     = db.query(Call).count()
    completed = db.query(Call).filter(Call.status == "completed").count()
    failed    = db.query(Call).filter(Call.status == "failed").count()
    initiated = db.query(Call).filter(Call.status == "initiated").count()
    return {"total": total, "completed": completed, "failed": failed, "initiated": initiated}


@router.get("/{call_id}", response_model=CallOut)
def get_call(call_id: int, db: Session = Depends(get_db)):
    c = db.query(Call).filter(Call.id == call_id).first()
    if not c:
        raise HTTPException(404, "Call not found")
    return c


@router.post("/", response_model=CallOut, status_code=201)
async def initiate_call(payload: CallCreate, db: Session = Depends(get_db)):
    """Initiate a Bland AI call for a company."""
    company = db.query(Company).filter(Company.id == payload.company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")

    # Build call task
    if payload.custom_task:
        task = payload.custom_task
    else:
        task = groq_service.generate_call_script(
            company_name=company.name,
            contact_name=company.contact_name or "the decision maker",
            industry=company.industry or "your industry",
            notes=company.notes or "",
        )

    first_sentence = (
        f"Hello, may I speak with {company.contact_name or 'the person in charge'}?"
        if company.contact_name else "Hello, is this a good time to talk?"
    )

    # Call Bland AI
    try:
        bland_resp = await bland_service.initiate_call(
            phone_number=payload.phone_number,
            task=task,
            first_sentence=first_sentence,
            voice=payload.voice or "maya",
            max_duration=payload.max_duration or 12,
        )
    except Exception as e:
        raise HTTPException(502, f"Bland AI error: {e}")

    bland_call_id = bland_resp.get("call_id", "")

    # Save to DB
    call = Call(
        company_id=payload.company_id,
        bland_call_id=bland_call_id,
        phone_number=payload.phone_number,
        task_prompt=task,
        status="initiated",
    )
    db.add(call)
    db.commit()
    db.refresh(call)

    # Notify
    detail = f"AI call initiated to *{company.name}*\n📞 {payload.phone_number}\nCall ID: {bland_call_id}"
    result = await notification_service.notify("call_initiated", detail)
    _log_notification(db, "call_initiated", detail, result)

    return call


@router.post("/{call_id}/sync")
async def sync_call_status(call_id: int, db: Session = Depends(get_db)):
    """Fetch latest status/transcript from Bland AI and update DB."""
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(404, "Call not found")
    if not call.bland_call_id:
        raise HTTPException(400, "No Bland call ID on record")

    try:
        data = await bland_service.get_call_details(call.bland_call_id)
    except Exception as e:
        raise HTTPException(502, f"Bland AI error: {e}")

    # Map Bland status
    bland_status = data.get("status", "unknown")
    if bland_status in ("completed", "complete"):
        call.status = "completed"
        call.completed_at = datetime.utcnow()
    elif bland_status in ("failed", "error"):
        call.status = "failed"
    else:
        call.status = bland_status

    call.duration      = data.get("call_length")
    call.transcript    = data.get("transcripts", [{}])[-1].get("text", "") if data.get("transcripts") else ""
    call.recording_url = data.get("recording_url", "")

    # Summarise transcript with Groq
    if call.transcript and call.status == "completed" and not call.summary:
        try:
            call.summary = groq_service.chat(
                [{"role": "user", "content": f"Summarise this sales call transcript in 3 bullet points:\n\n{call.transcript}"}],
                max_tokens=300,
            )
        except Exception:
            pass

    db.commit()
    db.refresh(call)
    return {"status": call.status, "duration": call.duration, "summary": call.summary}


@router.delete("/{call_id}")
async def stop_call(call_id: int, db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(404, "Call not found")
    if call.bland_call_id:
        try:
            await bland_service.stop_call(call.bland_call_id)
        except Exception:
            pass
    call.status = "failed"
    db.commit()
    return {"detail": "Call stopped"}
