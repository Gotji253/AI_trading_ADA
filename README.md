# AI_trading_ADA

Hermes Agent for **Cardano (ADA) only**  
Technical signals + **AI Analysis** (free OpenRouter model) + Paper Trading.

## Quick Start

```bash
git clone https://github.com/Gotji253/AI_trading_ADA.git
cd AI_trading_ADA
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add OPENROUTER_API_KEY (and optional BINANCE keys)
```

## Commands

```bash
python -m src.cli status
python -m src.cli ada-price
python -m src.cli ada-signal --interval 1h
python -m src.cli ai-analyze --interval 1h
python -m src.cli ai-analyze --interval 1h --model google/gemma-2-9b-it:free
python -m src.cli paper-status
python -m src.cli paper-auto --interval 1h
```

## AI Analysis & Model Switching

- Default model: `meta-llama/llama-3.1-8b-instruct:free` (free on OpenRouter)
- Change model permanently: set `OPENROUTER_MODEL=...` in `.env`
- Change model for one run: `--model <model-id>`

Popular free models:
- `meta-llama/llama-3.1-8b-instruct:free`
- `google/gemma-2-9b-it:free`
- `mistralai/mistral-7b-instruct:free`

## Paper Trading

Virtual 10,000 USDT. No real money.

## Hermes Skill

```bash
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-trader ~/.hermes/skills/finance/
```

## Safety

Paper mode only. Live trading is not implemented.
