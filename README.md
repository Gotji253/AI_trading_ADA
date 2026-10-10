# AI_trading_ADA

Hermes Agent specialized for trading **only Cardano (ADA)**.

## Hermes Skill (Ready to Run)

Copy or symlink the skill folder into Hermes:

```bash
# Example: install skill into Hermes skills directory
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-trader ~/.hermes/skills/finance/
```

Then in Hermes:

```
/ada-trader
```

or just ask: "วิเคราะห์สัญญาณ ADA ตอนนี้"

The skill will run:

```bash
python -m src.cli ada-signal --interval 1h
```

## Local Test

```bash
pip install -r requirements.txt
python -m src.cli ada-price
python -m src.cli ada-signal --interval 1h
```

## Project Structure

- `src/data/ada_price.py` — price & OHLCV fetcher (Binance / CoinGecko)
- `src/signals/ada_signals.py` — RSI + EMA + MACD signal generator
- `src/cli.py` — CLI for Hermes skill
- `skills/ada-trader/SKILL.md` — Hermes skill definition

## Safety

Analysis and paper mode only by default. No live trading without explicit confirmation.
