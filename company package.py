"""Companies router — CRUD, CSV import, Groq lead scoring, notifications."""
import io
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models import Company, Notification
from services import groq_service, notification_service

router = APIRouter(prefix="/companies", tags=["companies"])


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = ""
    contact_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    website: Optional[str] = ""
    address: Optional[str] = ""
    notes: Optional[str] = ""

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    lead_score: Optional[float] = None

class CompanyOut(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    contact_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    lead_score: float
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Helper ───────────────────────────────────────────────────────────────────

async def _auto_score_and_notify(company: Company, db: Session, is_new: bool = False):
    """Score lead with Groq; fire WhatsApp/Instagram notifications."""
    try:
        data = {
            "name": company.name,
            "industry": company.industry,
            "email": company.email,
            "phone": company.phone,
            "website": company.website,
            "notes": company.notes,
        }
        score = groq_service.score_lead(data)
        company.lead_score = score
        db.commit()
        db.refresh(company)
    except Exception:
        score = company.lead_score or 0.0

    # Notify: company added
    if is_new:
        detail = f"New company: *{company.name}*\nIndustry: {company.industry or 'N/A'}\nContact: {company.contact_name or 'N/A'}"
        result = await notification_service.notify("company_added", detail)
        _log_notification(db, "company_added", detail, result)

    # Notify: hot lead
    if score >= 80:
        detail = f"🔥 *{company.name}* scored {score:.0f}/100\nContact: {company.contact_name or 'N/A'} | {company.email or 'N/A'}"
        result = await notification_service.notify("hot_lead", detail)
        _log_notification(db, "hot_lead", detail, result)


def _log_notification(db: Session, event_type: str, message: str, result: dict):
    statuses = [v.get("status", "failed") for v in result.values() if isinstance(v, dict)]
    status = "sent" if any(s == "sent" for s in statuses) else "skipped"
    notif = Notification(
        type=event_type,
        message=message,
        platform="both",
        status=status,
        sent_at=datetime.utcnow() if status == "sent" else None,
    )
    db.add(notif)
    db.commit()


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[CompanyOut])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Company)
    if status:
        q = q.filter(Company.status == status)
    if search:
        q = q.filter(
            (Company.name.ilike(f"%{search}%")) |
            (Company.contact_name.ilike(f"%{search}%")) |
            (Company.email.ilike(f"%{search}%"))
        )
    if min_score is not None:
        q = q.filter(Company.lead_score >= min_score)
    return q.order_by(Company.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/stats")
def company_stats(db: Session = Depends(get_db)):
    total      = db.query(Company).count()
    hot_leads  = db.query(Company).filter(Company.lead_score >= 80).count()
    by_status  = {}
    for row in db.query(Company.status, Company).all():
        pass
    statuses = db.query(Company.status).distinct().all()
    for (s,) in statuses:
        by_status[s] = db.query(Company).filter(Company.status == s).count()
    return {
        "total": total,
        "hot_leads": hot_leads,
        "by_status": by_status,
    }


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    return c


@router.post("/", response_model=CompanyOut, status_code=201)
async def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    company = Company(**payload.model_dump(), lead_score=0.0, status="new")
    db.add(company)
    db.commit()
    db.refresh(company)
    await _auto_score_and_notify(company, db, is_new=True)
    db.refresh(company)
    return company


@router.put("/{company_id}", response_model=CompanyOut)
async def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db)):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(c, field, value)
    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    db.delete(c)
    db.commit()
    return {"detail": "Deleted"}


@router.post("/{company_id}/rescore")
async def rescore_company(company_id: int, db: Session = Depends(get_db)):
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(404, "Company not found")
    await _auto_score_and_notify(c, db, is_new=False)
    db.refresh(c)
    return {"lead_score": c.lead_score}


@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import companies from a CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "File must be a .csv")

    content = await file.read()
    try:
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(400, f"CSV parse error: {e}")

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    required = {"name"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(400, "CSV must have at least a 'name' column")

    created, skipped = 0, 0
    for _, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        if not name:
            skipped += 1
            continue
        # Skip duplicates
        exists = db.query(Company).filter(Company.name.ilike(name)).first()
        if exists:
            skipped += 1
            continue

        company = Company(
            name=name,
            industry=str(row.get("industry", "") or "").strip(),
            contact_name=str(row.get("contact_name", "") or "").strip(),
            email=str(row.get("email", "") or "").strip(),
            phone=str(row.get("phone", "") or "").strip(),
            website=str(row.get("website", "") or "").strip(),
            address=str(row.get("address", "") or "").strip(),
            notes=str(row.get("notes", "") or "").strip(),
            lead_score=0.0,
            status="new",
        )
        db.add(company)
        created += 1

    db.commit()

    # Notify import
    detail = f"CSV import complete: *{created}* companies added, {skipped} skipped."
    result = await notification_service.notify("csv_imported", detail)
    _log_notification(db, "csv_imported", detail, result)

    return {"created": created, "skipped": skipped}
