# AI_trading_ADA

Hermes Agent specialized for **Cardano (ADA) only**.

## Quick Start (Ready after adding API keys)

1. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/Gotji253/AI_trading_ADA.git
   cd AI_trading_ADA
   pip install -r requirements.txt
   ```

2. Copy and fill API keys:
   ```bash
   cp .env.example .env
   # Edit .env — put your BINANCE_API_KEY and BINANCE_API_SECRET
   ```

3. Check status:
   ```bash
   python -m src.cli status
   ```

4. Run analysis / signal:
   ```bash
   python -m src.cli ada-price
   python -m src.cli ada-signal --interval 1h
   ```

## API Keys Needed

| Key | Required? | Purpose |
|-----|-----------|---------|
| `BINANCE_API_KEY` + `BINANCE_API_SECRET` | Recommended | Higher rate limits + future trading. Public data works without keys. |
| `OPENROUTER_API_KEY` or `OPENAI_API_KEY` | Optional | Only if you run Hermes LLM from this environment. Hermes usually has its own config. |

**Safety default:** `TRADING_MODE=paper`  
Live trading is **not** enabled yet. Keys are used for data access.

## Hermes Skill

```bash
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-trader ~/.hermes/skills/finance/
```

Then in Hermes: `/ada-trader` or ask about ADA analysis.

## Project Structure

- `src/config.py` — loads `.env`
- `src/data/ada_price.py` — price & OHLCV
- `src/signals/ada_signals.py` — signal generator
- `src/cli.py` — CLI (`status`, `ada-price`, `ada-signal`)
- `skills/ada-trader/SKILL.md` — Hermes skill
- `.env.example` — template for keys

## Notes

- Without Binance keys the public endpoints still work (rate-limited).
- Live order placement is intentionally not implemented yet.
- Always start with paper mode.
