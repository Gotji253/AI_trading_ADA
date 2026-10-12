#!/bin/bash
# Quick setup script for Hermes + AI_trading_ADA
# ใช้งาน: bash scripts/setup_hermes.sh

set -e

echo "=== AI_trading_ADA Hermes Setup ==="

# 1. Create skill directory
mkdir -p ~/.hermes/skills/finance
echo "Created ~/.hermes/skills/finance"

# 2. Copy skill
if [ -d "skills/ada-api" ]; then
  cp -r skills/ada-api ~/.hermes/skills/finance/
  echo "Copied ada-api skill"
else
  echo "Warning: skills/ada-api not found"
fi

# 3. Check .env
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from example"
    echo "Please edit .env and add your API keys:"
    echo "  - OPENROUTER_API_KEY"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_CHAT_ID"
  fi
else
  echo ".env already exists"
fi

echo ""
echo "=== Setup Complete ==="
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
echo "3. In Hermes, type: /ada-api"
