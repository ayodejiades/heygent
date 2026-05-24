#!/bin/bash
# ============================================================
# HeyGent Dual-Agent System — Startup Script
# Boots up both the FastAPI python backends and the Next.js frontend
# ============================================================

# Color formatting
TEAL='\033[0;36m'
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${TEAL}"
echo "  _    _           _____            _"
echo " | |  | |         / ____|          | |"
echo " | |__| | ___ _ _| |  __  ___ _ __ | |_"
echo " |  __  |/ _ \ '_ \ | |_ |/ _ \ '_ \| __|"
echo " | |  | |  __/ | | | |__| |  __/ | | | |_"
echo " |_|  |_|\___|_| |_|\_____|\___|_| |_|\__|"
echo -e "${NC}"
echo -e "${PURPLE}=== BCT x DSN Hackathon 3.0 Agent Showcase ===${NC}\n"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}[Warning] No .env file found in root directory.${NC}"
fi

# Detect .venv
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}[1/3] Activating Python Virtual Environment...${NC}"
    source "$VENV_DIR/bin/activate"
else
    echo -e "${YELLOW}[Info] No .venv found in root directory. Attempting to run global python...${NC}"
fi

# Boot up FastAPI Backend
echo -e "${GREEN}[2/3] Launching FastAPI backend agent service...${NC}"
echo -e "${TEAL}Host: http://127.0.0.1:8000${NC}"
echo -e "Logs streaming to backend.log..."

# Move to backend directory and start uvicorn
cd backend || exit
uvicorn api.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a second and check if backend is running
sleep 2
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓ FastAPI backend is running! (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Backend failed to start. Please check backend.log for details.${NC}"
    echo -e "${YELLOW}[Tip] Offline Sandbox Mode is active in the frontend, so the UI will still function fully!${NC}"
fi

# Launch Next.js Frontend
echo -e "${GREEN}[3/3] Launching Next.js frontend dev server...${NC}"
echo -e "${TEAL}URL: http://localhost:3000${NC}"
echo -e "Press Ctrl+C to terminate both servers."

# Trap Ctrl+C to kill the backend too
cleanup() {
    echo -e "\n${YELLOW}Stopping FastAPI backend (PID: $BACKEND_PID)...${NC}"
    kill $BACKEND_PID 2>/dev/null
    echo -e "${GREEN}Cleaned up successfully. Goodbye!${NC}"
    exit 0
}
trap cleanup SIGINT

# Move to frontend directory and run next dev
cd frontend || exit
npm run dev

# If next dev exits, clean up backend
cleanup
