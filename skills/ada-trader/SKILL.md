---
name: ada-trader
description: Analyze Cardano (ADA) only and generate buy/sell/hold signals with RSI, EMA, MACD, stop-loss and take-profit. Use when the user asks about ADA price, trading signal, or analysis.
version: 1.0.0
author: AI_trading_ADA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ADA, Cardano, Trading, Crypto, Signals]
    category: finance
    requires_toolsets: [terminal]
---

# ADA Trader Skill

Specialized for **ADA (Cardano) only**. Never analyze or trade other coins.

## When to Use

- User asks for ADA price, analysis, signal, buy/sell recommendation
- User wants current market view or technical levels for ADA

## Prerequisites

The project root (this repo) must be on the machine and Python dependencies installed:

```bash
pip install -r requirements.txt
```

## How to Run

Use the `terminal` tool to run the CLI from the repo root:

```bash
python -m src.cli ada-signal --interval 1h
```

Optional flags:
- `--interval 15m|1h|4h|1d`
- `--source binance|coingecko`

## Procedure

1. Run the command above with `terminal`.
2. Parse the JSON output.
3. Present a short Thai summary + the key numbers (price, signal, confidence, RSI, stop-loss, take-profit).
4. Always remind that this is analysis / paper only — no live orders without explicit confirmation.

## Output Example

The CLI returns JSON like:

```json
{
  "status": "ok",
  "symbol": "ADA",
  "signal": "buy",
  "confidence": 0.6,
  "price": 0.452,
  "rsi": 28.4,
  "stop_loss": 0.43,
  "take_profit": 0.48,
  "reasons": ["RSI oversold"]
}
```

## Safety

- ADA only. Refuse other assets.
- Default is analysis / paper. Never place live orders unless the user explicitly confirms.
- If data fetch fails, report the error clearly.
