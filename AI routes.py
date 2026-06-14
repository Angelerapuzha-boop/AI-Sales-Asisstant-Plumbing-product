"""AI router — direct Groq Llama-3 endpoints."""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import groq_service

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str
    system: Optional[str] = "You are a helpful AI sales assistant."
    temperature: Optional[float] = 0.7


class ScoreRequest(BaseModel):
    company_name: str
    industry: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    website: Optional[str] = ""
    notes: Optional[str] = ""


class CallScriptRequest(BaseModel):
    company_name: str
    contact_name: Optional[str] = "the decision maker"
    industry: Optional[str] = ""
    notes: Optional[str] = ""


class EmailDraftRequest(BaseModel):
    company_name: str
    contact_name: Optional[str] = "Sir/Madam"
    industry: Optional[str] = ""
    notes: Optional[str] = ""
    sender_name: Optional[str] = "Sales Team"


@router.post("/chat")
def chat(payload: ChatRequest):
    try:
        reply = groq_service.chat(
            messages=[{"role": "user", "content": payload.message}],
            system=payload.system or "",
            temperature=payload.temperature or 0.7,
        )
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(502, f"Groq error: {e}")


@router.post("/score")
def score_lead(payload: ScoreRequest):
    try:
        score = groq_service.score_lead(payload.model_dump())
        return {"score": score}
    except Exception as e:
        raise HTTPException(502, f"Groq error: {e}")


@router.post("/call-script")
def generate_call_script(payload: CallScriptRequest):
    try:
        script = groq_service.generate_call_script(
            company_name=payload.company_name,
            contact_name=payload.contact_name or "the decision maker",
            industry=payload.industry or "",
            notes=payload.notes or "",
        )
        return {"script": script}
    except Exception as e:
        raise HTTPException(502, f"Groq error: {e}")


@router.post("/draft-email")
def draft_email(payload: EmailDraftRequest):
    try:
        result = groq_service.generate_sales_email(
            company_name=payload.company_name,
            contact_name=payload.contact_name or "Sir/Madam",
            industry=payload.industry or "",
            notes=payload.notes or "",
            sender_name=payload.sender_name or "Sales Team",
        )
        return result
    except Exception as e:
        raise HTTPException(502, f"Groq error: {e}")


@router.get("/models")
def list_models():
    return {
        "active_model": groq_service.settings.GROQ_MODEL,
        "available": [
            "llama-3.3-70b-versatile",
            "llama3-8b-8192",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
        ],
    }
