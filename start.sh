#!/bin/bash
# ============================================================
#  Inventory Management Agent — Unified Startup Script
# ============================================================
#  Starts the Flask API server and opens the frontend.
#
#  Usage:
#     ./start.sh          # Start API + open dashboard
#     ./start.sh api       # Start API only
#     ./start.sh test      # Run API test suite
#     ./start.sh cli       # Run CLI agent (no API)
#
#  On Windows use start.bat instead, or run in Git Bash / WSL.
# ============================================================

set -e

# ── Paths ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/Dummy Agent Folder"
FRONTEND_DIR="$SCRIPT_DIR/Frontend"

# ── Colors ──
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=================================================="
echo "  Inventory Management Agent — Startup"
echo "=================================================="
echo ""

# ── Create venv if needed ──
if [ ! -d "$AGENT_DIR/venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv "$AGENT_DIR/venv"
    echo -e "${GREEN}✅ venv created${NC}"
else
    echo -e "${GREEN}✅ venv exists${NC}"
fi

# ── Install dependencies ──
echo -e "${CYAN}Installing dependencies...${NC}"
"$AGENT_DIR/venv/bin/pip" install -r "$AGENT_DIR/requirements.txt" > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}"

# ── Determine action ──
ACTION="${1:-all}"

case "$ACTION" in
    api)
        echo -e "${CYAN}Starting API server on http://localhost:5000${NC}"
        echo ""
        "$AGENT_DIR/venv/bin/python" "$AGENT_DIR/api.py"
        ;;

    test)
        echo -e "${CYAN}Running API tests...${NC}"
        echo ""
        "$AGENT_DIR/venv/bin/python" "$AGENT_DIR/test_api.py"
        ;;

    cli)
        echo -e "${CYAN}Running CLI agent...${NC}"
        echo ""
        "$AGENT_DIR/venv/bin/python" "$AGENT_DIR/agent.py"
        ;;

    all|*)
        # ── Start API in background ──
        echo -e "${CYAN}Starting API server on http://localhost:5000${NC}"
        "$AGENT_DIR/venv/bin/python" "$AGENT_DIR/api.py" &
        API_PID=$!

        # ── Wait for server to be ready ──
        echo -e "${YELLOW}Waiting for server...${NC}"
        for i in $(seq 1 10); do
            if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
                echo -e "${GREEN}✅ API server is ready${NC}"
                break
            fi
            sleep 1
        done

        # ── Open frontend ──
        echo ""
        echo -e "${GREEN}==================================================${NC}"
        echo -e "${GREEN}  Everything is running!${NC}"
        echo -e "${GREEN}==================================================${NC}"
        echo ""
        echo "  API Server : http://localhost:5000"
        echo "  Dashboard  : $FRONTEND_DIR/index.html"
        echo ""
        echo "  Tool pages:"
        echo "    1. Order       → order.html"
        echo "    2. Inventory   → inventory.html"
        echo "    3. Payment     → payment.html"
        echo "    4. Invoice     → invoice.html"
        echo "    5. Delivery    → delivery.html"
        echo "    6. Notification→ notification.html"
        echo ""
        echo -e "${YELLOW}  Press Ctrl+C to stop the server${NC}"
        echo ""

        # Try to open in browser
        if command -v xdg-open > /dev/null 2>&1; then
            xdg-open "$FRONTEND_DIR/index.html"
        elif command -v open > /dev/null 2>&1; then
            open "$FRONTEND_DIR/index.html"
        elif command -v start > /dev/null 2>&1; then
            start "$FRONTEND_DIR/index.html"
        else
            echo "  Open the frontend manually in your browser."
        fi

        # ── Keep running ──
        wait $API_PID
        ;;
esac
