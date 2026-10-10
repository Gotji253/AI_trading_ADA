# AI_trading_ADA

Hermes Agent for **Cardano (ADA) only** with **Paper Trading**.

## Quick Start

```bash
git clone https://github.com/Gotji253/AI_trading_ADA.git
cd AI_trading_ADA
pip install -r requirements.txt
cp .env.example .env
# (optional) add Binance keys to .env
```

## Commands

```bash
python -m src.cli status
python -m src.cli ada-price
python -m src.cli ada-signal --interval 1h
python -m src.cli paper-status
python -m src.cli paper-auto --interval 1h
python -m src.cli paper-history
```

## Paper Trading

- Starts with 10,000 USDT virtual balance
- Opens long on buy signal / short on sell signal when flat
- Closes position on opposite signal
- State saved in `data/paper_state.json` (gitignored)
- **No real money is ever used**

## Hermes Skill

```bash
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-trader ~/.hermes/skills/finance/
```

Then: `/ada-trader` or ask for ADA paper trading.

## Safety

Default mode is paper. Live trading is not implemented.
