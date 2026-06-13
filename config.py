import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

class Settings:
    # Groq AI
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Bland AI
    BLAND_AI_API_KEY: str = os.getenv("BLAND_AI_API_KEY", "")
    BLAND_AI_BASE_URL: str = os.getenv("BLAND_AI_BASE_URL", "https://api.bland.ai/v1")

    # Google Calendar
    GOOGLE_CALENDAR_API_KEY: str = os.getenv("GOOGLE_CALENDAR_API_KEY", "")
    GOOGLE_CALENDAR_CLIENT_ID: str = os.getenv("GOOGLE_CALENDAR_CLIENT_ID", "")
    GOOGLE_CALENDAR_CLIENT_SECRET: str = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", "")

    # Gmail
    GMAIL_API_KEY: str = os.getenv("GMAIL_API_KEY", "")
    GMAIL_CLIENT_ID: str = os.getenv("GMAIL_CLIENT_ID", "")
    GMAIL_CLIENT_SECRET: str = os.getenv("GMAIL_CLIENT_SECRET", "")
    GMAIL_SENDER_EMAIL: str = os.getenv("GMAIL_SENDER_EMAIL", "")

    # WhatsApp
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_RECIPIENT_NUMBER: str = os.getenv("WHATSAPP_RECIPIENT_NUMBER", "")

    # Instagram
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    INSTAGRAM_RECIPIENT_ID: str = os.getenv("INSTAGRAM_RECIPIENT_ID", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sales_crm.db")

    # Server
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8501")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

    GOOGLE_SCOPES: list = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.compose",
        "openid",
        "email",
        "profile",
    ]

settings = Settings()
