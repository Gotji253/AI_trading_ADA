---
name: ada-trader
description: Analyze Cardano (ADA) only and generate buy/sell/hold signals with RSI, EMA, MACD. Use when the user asks about ADA price, trading signal, or analysis. Requires the AI_trading_ADA repo on the machine.
version: 1.1.0
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

**ADA only.** Never analyze or trade other coins.

## When to Use

User asks for ADA price, analysis, signal, or market view.

## Prerequisites

1. This repo is cloned and `pip install -r requirements.txt` has been run.
2. `.env` file exists with at least `BINANCE_API_KEY` and `BINANCE_API_SECRET` (recommended).
3. Working directory is the repo root (or PYTHONPATH includes it).

## How to Run

Use the `terminal` tool:

```bash
# Check keys and mode
python -m src.cli status

# Get signal
python -m src.cli ada-signal --interval 1h
```

## Procedure

1. Optionally run `status` first to confirm keys are loaded.
2. Run `ada-signal` (or `ada-price`).
3. Parse the JSON.
4. Reply with a short Thai summary including price, signal, confidence, RSI, stop-loss, take-profit.
5. Remind that current mode is analysis/paper — no live orders without explicit user confirmation.

## Safety

- ADA only.
- Default `TRADING_MODE=paper`.
- Do not place live orders.
