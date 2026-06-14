#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
# AI Sales CRM — Local Run Script (no Docker needed)
# Usage:  chmod +x run.sh && ./run.sh
# ─────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  🤖 AI Sales CRM — Starting up              ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ── Check Python ──────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}❌ Python 3 not found. Install Python 3.10+ and re-run.${NC}"
  exit 1
fi

# ── Install backend deps ──────────────────────────────────
echo -e "\n${GREEN}📦 Installing backend dependencies…${NC}"
cd "$BACKEND"
python3 -m pip install -q -r requirements.txt

# ── Install frontend deps ─────────────────────────────────
echo -e "\n${GREEN}📦 Installing frontend dependencies…${NC}"
cd "$FRONTEND"
python3 -m pip install -q -r requirements.txt

# ── Start backend ─────────────────────────────────────────
echo -e "\n${GREEN}🚀 Starting FastAPI backend on http://localhost:8000 …${NC}"
cd "$BACKEND"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
echo -n "   Waiting for backend"
for i in {1..20}; do
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e " ${GREEN}✅ Ready!${NC}"
    break
  fi
  echo -n "."
  sleep 1
done

# ── Start frontend ────────────────────────────────────────
echo -e "\n${GREEN}🎨 Starting Streamlit frontend on http://localhost:8501 …${NC}"
cd "$FRONTEND"
BACKEND_URL=http://localhost:8000 \
python3 -m streamlit run app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false \
  --browser.serverAddress=localhost &
FRONTEND_PID=$!

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ AI Sales CRM is running!${NC}"
echo -e "   🎨 Frontend:  http://localhost:8501"
echo -e "   ⚙️  Backend:   http://localhost:8000"
echo -e "   📖 API Docs:  http://localhost:8000/docs"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "   Press Ctrl+C to stop both servers\n"

# Trap Ctrl+C
cleanup() {
  echo -e "\n${RED}Stopping servers…${NC}"
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}
trap cleanup INT TERM

wait
