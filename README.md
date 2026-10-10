# AI_trading_ADA

Hermes Agent for **Cardano (ADA) only** with learning from paper trades.

## Features

- Technical signals + Multi-timeframe
- Support/Resistance, News, On-chain (Koios)
- AI analysis (free OpenRouter models)
- Paper trading with SL/TP, stats, Telegram alerts (Thai)
- **Trade memory + Hermes learning skill**
- Hourly analysis runner

## Quick Start

```bash
git clone https://github.com/Gotji253/AI_trading_ADA.git
cd AI_trading_ADA
pip install -r requirements.txt
cp .env.example .env
# Add OPENROUTER_API_KEY + TELEGRAM keys if wanted
```

## Learning from Trades (Hermes)

```bash
# 1. Generate some paper trades
python -m src.cli paper-auto

# 2. Update memory
python -m src.cli memory

# 3. In Hermes
/ada-learn
```

Or generate a ready prompt:
```bash
python -m src.cli learn-prompt
```

See `docs/hermes-learning.md` and `skills/ada-learn/SKILL.md`.

## Other Commands

```bash
python -m src.cli hourly
python -m src.cli multi-tf
python -m src.cli paper-status
```

## Safety

Paper mode only. No live trading.
