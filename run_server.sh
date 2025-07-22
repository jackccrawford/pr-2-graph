#!/bin/bash

# pr-2-graph Server Runner
# Follows TIN Node Communications pattern for consistent deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 pr-2-graph Server Startup${NC}"
echo "=================================="

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry is not installed. Please install Poetry first.${NC}"
    exit 1
fi

# Load environment variables
if [ -f ".env.local" ]; then
    echo -e "${GREEN}📄 Loading .env.local configuration${NC}"
    export $(grep -v '^#' .env.local | xargs)
elif [ -f ".env" ]; then
    echo -e "${YELLOW}📄 Loading .env configuration${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}❌ No .env or .env.local file found${NC}"
    exit 1
fi

# Set defaults if not provided
PORT=${PORT:-7700}
HOST=${HOST:-0.0.0.0}
DEBUG=${DEBUG:-true}

echo -e "${GREEN}🔧 Configuration:${NC}"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Debug: $DEBUG"
echo "  Primary Model: ${PRIMARY_MODEL:-'not set'}"
echo "  Critic Model: ${CRITIC_MODEL:-'not set'}"
echo ""

# Check if Ollama is running
echo -e "${BLUE}🤖 Checking Ollama status...${NC}"
if ! curl -s "${OLLAMA_BASE_URL:-http://localhost:11434}/api/tags" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama not responding at ${OLLAMA_BASE_URL:-http://localhost:11434}${NC}"
    echo -e "${YELLOW}   Make sure Ollama is running: ollama serve${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Ollama is running${NC}"
    echo ""
fi

# Install dependencies if needed
if [ ! -d ".venv" ] || [ ! -f "poetry.lock" ]; then
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    poetry install --no-root
    echo ""
fi

# Start the server
echo -e "${GREEN}🌟 Starting pr-2-graph server...${NC}"
echo -e "${BLUE}   URL: http://$HOST:$PORT${NC}"
echo -e "${BLUE}   API Docs: http://$HOST:$PORT/docs${NC}"
echo -e "${BLUE}   Health: http://$HOST:$PORT/health${NC}"
echo ""

# Handle different run modes
if [ "$1" = "--dev" ]; then
    echo -e "${YELLOW}🔧 Development mode with auto-reload${NC}"
    poetry run uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
elif [ "$1" = "--prod" ]; then
    echo -e "${GREEN}🚀 Production mode${NC}"
    poetry run uvicorn app.main:app --host "$HOST" --port "$PORT" --workers 4
else
    echo -e "${BLUE}🔄 Standard mode with auto-reload${NC}"
    echo -e "${YELLOW}   Use --prod for production mode${NC}"
    echo -e "${YELLOW}   Use --dev for explicit development mode${NC}"
    echo ""
    poetry run uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
fi
