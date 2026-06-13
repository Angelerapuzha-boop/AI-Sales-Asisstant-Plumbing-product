from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Company(Base):
    __tablename__ = "companies"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(255), nullable=False)
    industry     = Column(String(100))
    contact_name = Column(String(255))
    email        = Column(String(255))
    phone        = Column(String(50))
    website      = Column(String(255))
    address      = Column(Text)
    lead_score   = Column(Float, default=0.0)
    status       = Column(String(50), default="new")      # new | contacted | qualified | proposal | closed
    notes        = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    calls    = relationship("Call",    back_populates="company", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="company", cascade="all, delete-orphan")
    emails   = relationship("Email",   back_populates="company", cascade="all, delete-orphan")


class Call(Base):
    __tablename__ = "calls"

    id            = Column(Integer, primary_key=True, index=True)
    company_id    = Column(Integer, ForeignKey("companies.id"), nullable=False)
    bland_call_id = Column(String(255))
    phone_number  = Column(String(50))
    task_prompt   = Column(Text)
    status        = Column(String(50), default="initiated")   # initiated | in_progress | completed | failed
    duration      = Column(Integer)                           # seconds
    transcript    = Column(Text)
    recording_url = Column(String(500))
    summary       = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)
    completed_at  = Column(DateTime)

    company = relationship("Company", back_populates="calls")


class Meeting(Base):
    __tablename__ = "meetings"

    id               = Column(Integer, primary_key=True, index=True)
    company_id       = Column(Integer, ForeignKey("companies.id"), nullable=False)
    calendar_event_id = Column(String(255))
    title            = Column(String(255))
    description      = Column(Text)
    start_time       = Column(DateTime)
    end_time         = Column(DateTime)
    attendees        = Column(JSON)                   # list of email strings
    meet_link        = Column(String(500))
    status           = Column(String(50), default="scheduled")  # scheduled | completed | cancelled
    reminders_sent   = Column(JSON, default=list)    # ["24h", "1h", "10min"]
    created_at       = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="meetings")


class Email(Base):
    __tablename__ = "emails"

    id               = Column(Integer, primary_key=True, index=True)
    company_id       = Column(Integer, ForeignKey("companies.id"), nullable=False)
    subject          = Column(String(500))
    body             = Column(Text)
    recipient_email  = Column(String(255))
    gmail_message_id = Column(String(255))
    status           = Column(String(50), default="generated")  # generated | sent | failed
    created_at       = Column(DateTime, default=datetime.utcnow)
    sent_at          = Column(DateTime)

    company = relationship("Company", back_populates="emails")


class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True, index=True)
    type       = Column(String(100))    # company_added | hot_lead | email_generated | email_sent | ...
    message    = Column(Text)
    platform   = Column(String(50))     # whatsapp | instagram | both
    status     = Column(String(50), default="pending")    # pending | sent | failed
    error_msg  = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at    = Column(DateTime)


class GoogleToken(Base):
    """Stores Google OAuth tokens (Calendar + Gmail combined)."""
    __tablename__ = "google_tokens"

    id            = Column(Integer, primary_key=True, index=True)
    service       = Column(String(50), unique=True)   # "google"
    access_token  = Column(Text)
    refresh_token = Column(Text)
    token_uri     = Column(String(500))
    client_id     = Column(String(500))
    client_secret = Column(String(500))
    scopes        = Column(JSON)
    expiry        = Column(DateTime)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
