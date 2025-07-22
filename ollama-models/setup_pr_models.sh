#!/bin/bash

# Setup custom PR analysis models for pr-2-graph
# Inspired by tin-sidekick-sdr pattern

set -e

echo "🤖 Setting up pr-2-graph custom Ollama models..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create pr-analyzer model
echo -e "${BLUE}Creating pr-analyzer model...${NC}"
cd pr-analyzer
ollama create pr-analyzer -f Modelfile
cd ..

# Create pr-critic model  
echo -e "${BLUE}Creating pr-critic model...${NC}"
cd pr-critic
ollama create pr-critic -f Modelfile
cd ..

# Create pr-formatter model
echo -e "${BLUE}Creating pr-formatter model...${NC}"
cd pr-formatter
ollama create pr-formatter -f Modelfile
cd ..

echo -e "${GREEN}✅ All pr-2-graph models created successfully!${NC}"
echo ""
echo "Available models:"
echo "  - pr-analyzer:latest   (Primary analysis - gemma3n:e2b base)"
echo "  - pr-critic:latest     (Quality review - qwen3:1.7b base)"
echo "  - pr-formatter:latest  (JSON formatting - phi4-mini:3.8b base)"
echo ""
echo "Update your .env.local to use these models:"
echo "  PRIMARY_MODEL=pr-analyzer:latest"
echo "  CRITIC_MODEL=pr-critic:latest"
echo "  FORMATTER_MODEL=pr-formatter:latest"
