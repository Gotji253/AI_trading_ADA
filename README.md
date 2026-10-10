# AI_trading_ADA

Hermes Agent + **Multi-Agent** (Manager / Alpha / Risk / Execution) สำหรับ ADA

## Features

- Multi-Timeframe signals + Support/Resistance
- Paper trading พร้อม risk controls
- Telegram alerts (ภาษาไทย)
- **Multi-Agent via FastAPI**
- Hermes learning skill
- **Backtest & Walk-Forward Validation**

## Quick Start

```bash
git clone https://github.com/Gotji253/AI_trading_ADA.git
cd AI_trading_ADA
pip install -r requirements.txt
cp .env.example .env
```

## รันแบบ CLI (เดิม)

```bash
python -m src.cli paper-auto
python -m src.cli daily-summary
```

## รันแบบ Multi-Agent (FastAPI)

```bash
uvicorn src.api.main:app --reload --port 8000
```

## รัน Backtest

```bash
python -m src.backtest.cli --mode simple --limit 500
python -m src.backtest.cli --mode walkforward --limit 800
```

ดูรายละเอียดที่ `docs/backtest.md` และ `docs/multi-agent.md`

## Safety

Paper mode only. No live trading.
