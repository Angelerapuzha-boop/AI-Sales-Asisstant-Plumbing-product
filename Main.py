"""FastAPI main — AI Sales CRM backend."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import init_db
from services import scheduler as sched_module
from routers import companies, calls, calendar_routes, email_routes, ai_routes, notifications


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    sched_module.start()
    yield
    # Shutdown
    sched_module.stop()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Sales CRM API",
    description="Groq AI + Bland AI + Google Calendar + Gmail + WhatsApp/Instagram",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(companies.router)
app.include_router(calls.router)
app.include_router(calendar_routes.router)
app.include_router(email_routes.router)
app.include_router(ai_routes.router)
app.include_router(notifications.router)


# ── Google OAuth callback (shared) ────────────────────────────────────────────

@app.get("/auth/google/callback", tags=["auth"])
def google_calendar_callback(code: str):
    from services import calendar_service
    try:
        calendar_service.exchange_code(code)
        return JSONResponse({"detail": "✅ Google Calendar connected! You can close this tab."})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/auth/google/callback_gmail", tags=["auth"])
def google_gmail_callback(code: str):
    from services import gmail_service
    try:
        gmail_service.exchange_code(code)
        return JSONResponse({"detail": "✅ Gmail connected! You can close this tab."})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
def health():
    from services import calendar_service, gmail_service
    return {
        "status": "ok",
        "google_calendar": calendar_service.is_authorized(),
        "gmail": gmail_service.is_authorized(),
        "scheduler": sched_module.scheduler.running,
    }


@app.get("/", tags=["health"])
def root():
    return {
        "name": "AI Sales CRM API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
