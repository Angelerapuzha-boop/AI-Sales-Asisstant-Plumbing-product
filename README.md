# 🤖 AI Sales CRM

**Groq Llama-3 · Bland AI · Google Calendar · Gmail · WhatsApp · Instagram**

A complete AI-powered sales CRM with automated phone calls, meeting scheduling,
email generation, and real-time WhatsApp/Instagram notifications.

---

## 🗂️ Project Structure

```
ai-sales-crm/
├── .env                        ← All API keys (edit this first)
├── docker-compose.yml          ← One-command Docker deployment
├── run.sh                      ← Local run without Docker
├── backend/
│   ├── main.py                 ← FastAPI app entry point
│   ├── config.py               ← Settings from .env
│   ├── database.py             ← SQLAlchemy + SQLite
│   ├── models.py               ← DB models
│   ├── requirements.txt
│   ├── routers/
│   │   ├── companies.py        ← CRUD + CSV import + lead scoring
│   │   ├── calls.py            ← Bland AI phone calls
│   │   ├── calendar_routes.py  ← Google Calendar events
│   │   ├── email_routes.py     ← Groq emails + Gmail sending
│   │   ├── ai_routes.py        ← Direct Groq AI access
│   │   └── notifications.py    ← WhatsApp + Instagram
│   └── services/
│       ├── groq_service.py     ← Groq Llama-3 calls
│       ├── bland_service.py    ← Bland AI async client
│       ├── calendar_service.py ← Google Calendar OAuth + API
│       ├── gmail_service.py    ← Gmail OAuth + API
│       ├── notification_service.py ← Meta WhatsApp/Instagram API
│       └── scheduler.py        ← APScheduler background jobs
└── frontend/
    ├── app.py                  ← Streamlit entry + sidebar
    ├── requirements.txt
    ├── utils/api_client.py     ← Backend HTTP client
    └── pages/
        ├── 1_📊_Dashboard.py
        ├── 2_🏢_Companies.py
        ├── 3_📞_AI_Calls.py
        ├── 4_📅_Meetings.py
        ├── 5_📧_Emails.py
        └── 6_⚙️_Settings.py
```

---

## ⚡ Quick Start

### Option A — Docker (recommended, zero-config)

```bash
# 1. Edit your .env (add your secrets)
nano .env

# 2. Build and start everything
docker-compose up --build

# 3. Open browser
# Frontend:  http://localhost:8501
# API docs:  http://localhost:8000/docs
```

### Option B — Local (without Docker)

```bash
# 1. Edit .env
nano .env

# 2. Run both servers with one command
chmod +x run.sh
./run.sh

# Or manually:
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
pip install -r requirements.txt
BACKEND_URL=http://localhost:8000 streamlit run app.py --server.port 8501
```

---

## 🔑 API Keys Setup

### 1 · Groq AI ✅ (Already configured)
Pre-configured in `.env`. Model: `llama-3.3-70b-versatile`

### 2 · Bland AI ✅ (Already configured)
Pre-configured in `.env`.

### 3 · Google Calendar + Gmail (needs client secret)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select / create a project
3. Enable **Google Calendar API** and **Gmail API**
4. Go to **Credentials → OAuth 2.0 Client IDs**
5. For Calendar client (`869844262487-sr7vaeatfj5q32hme113vd4p72iffak2`):
   - Add `http://localhost:8000/auth/google/callback` to authorized redirect URIs
   - Copy **Client Secret** → `GOOGLE_CALENDAR_CLIENT_SECRET` in `.env`
6. For Gmail client (`869844262487-1eecpn7til8ngp3a7ngc46lsdrf1ius2`):
   - Add `http://localhost:8000/auth/google/callback_gmail` to authorized redirect URIs
   - Copy **Client Secret** → `GMAIL_CLIENT_SECRET` in `.env`
7. In Streamlit → Settings page, click the OAuth connect links

### 4 · WhatsApp Business API

1. [Meta for Developers](https://developers.facebook.com) → Create App → WhatsApp
2. WhatsApp → API Setup → copy:
   - **Phone Number ID** → `WHATSAPP_PHONE_NUMBER_ID`
   - **Temporary / Permanent Access Token** → `WHATSAPP_ACCESS_TOKEN`
3. Your recipient phone (with country code) → `WHATSAPP_RECIPIENT_NUMBER`

### 5 · Instagram DM API

1. Connect Instagram Business account to Facebook Page in Meta Business Suite
2. Add Instagram Graph API to your Meta App
3. Request `instagram_manage_messages` permission
4. Copy:
   - **Instagram Business Account ID** → `INSTAGRAM_BUSINESS_ACCOUNT_ID`
   - **Access Token** → `INSTAGRAM_ACCESS_TOKEN`
   - Recipient Instagram User ID → `INSTAGRAM_RECIPIENT_ID`

---

## 🔔 Notification Triggers

| Trigger | Emoji | Event |
|---|---|---|
| New company added | 🏢 | Company Added |
| Lead score ≥ 80 | 🔥 | Hot Lead Alert |
| Email generated | 📧 | Email Generated |
| Email sent | ✅ | Email Sent |
| Meeting scheduled | 📅 | Meeting Scheduled |
| Meeting completed | ✅ | Meeting Completed |
| AI call made | 📞 | Call Initiated |
| CSV import done | 📤 | Import Completed |
| Daily at 6 PM UTC | 📊 | Daily Report |
| 24h before meeting | 🔔 | Meeting Reminder |
| 1h before meeting | ⏰ | Meeting Reminder |
| 10min before meeting | ⏰ | Meeting Reminder |

---

## 🚀 Cloud Hosting (Railway / Render)

### Railway (easiest)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and init
railway login
railway init

# Deploy backend
cd backend
railway up

# Deploy frontend (separate service)
cd ../frontend
railway up
```

Set environment variables in Railway dashboard from your `.env`.

### Render

1. Create two **Web Services** in Render
2. **Backend**: Root = `backend/`, Start = `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Frontend**: Root = `frontend/`, Start = `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
4. Add all env vars from `.env` in Render dashboard
5. Set `BACKEND_URL` in frontend service to the backend's Render URL

---

## 📡 API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | System health check |
| GET | `/docs` | Interactive API docs (Swagger) |
| GET/POST | `/companies/` | List / create companies |
| POST | `/companies/import/csv` | Bulk CSV import |
| POST | `/companies/{id}/rescore` | Re-score with Groq |
| GET/POST | `/calls/` | List / initiate calls |
| POST | `/calls/{id}/sync` | Sync from Bland AI |
| GET/POST | `/calendar/meetings` | List / create meetings |
| GET | `/calendar/auth` | Get Google OAuth URL |
| GET/POST | `/emails/` | List emails |
| POST | `/emails/generate` | Generate with Groq |
| POST | `/emails/{id}/send` | Send via Gmail |
| GET | `/emails/auth` | Get Gmail OAuth URL |
| POST | `/ai/chat` | Direct Groq chat |
| POST | `/notifications/test` | Test WhatsApp/Instagram |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit 1.29 |
| Backend | FastAPI 0.104 + Uvicorn |
| Database | SQLite (via SQLAlchemy) |
| AI | Groq Llama-3.3-70b-versatile |
| Phone calls | Bland AI |
| Calendar | Google Calendar API v3 |
| Email | Gmail API v1 |
| Notifications | Meta WhatsApp Business + Instagram Graph API |
| Scheduler | APScheduler 3.10 |
| Containerisation | Docker + Docker Compose |
