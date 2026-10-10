# AI_trading_ADA

Hermes Agent for **Cardano (ADA) only**

## Features

- Price + technical signals (RSI, EMA, MACD)
- Multi-timeframe (15m / 1h / 4h)
- **Support / Resistance** automatic levels
- **News + simple sentiment** (free sources)
- **Basic Cardano on-chain** via Koios (free, no key)
- AI analysis (free OpenRouter models)
- Paper trading with SL/TP, stats, equity curve
- **Trade memory** for AI learning
- **Hourly analysis** runner (for cron / Hermes)

## Quick Start

```bash
git clone https://github.com/Gotji253/AI_trading_ADA.git
cd AI_trading_ADA
pip install -r requirements.txt
cp .env.example .env
# Add OPENROUTER_API_KEY (and optional BINANCE keys)
```

## Useful Commands

```bash
python -m src.cli status
python -m src.cli multi-tf
python -m src.cli levels
python -m src.cli news
python -m src.cli onchain
python -m src.cli memory
python -m src.cli hourly          # full report
python -m src.cli ai-analyze
python -m src.cli paper-status
python -m src.cli paper-auto
```

## Hermes

See `docs/hermes-integration.md` for cron, memory, and skill creation notes.

```bash
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-trader ~/.hermes/skills/finance/
```

## Safety

Paper mode only. No live trading.
