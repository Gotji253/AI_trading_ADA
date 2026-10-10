---
name: ada-trader
description: Analyze ADA with technicals + AI reasoning and run paper trading. Use for ADA analysis, signals, or paper trading.
version: 1.3.0
author: AI_trading_ADA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ADA, Cardano, Trading, AI, Paper]
    category: finance
    requires_toolsets: [terminal]
---

# ADA Trader Skill

ADA only. Supports technical signals, AI analysis, and paper trading.

## Commands (via terminal)

```bash
python -m src.cli status
python -m src.cli ada-signal --interval 1h
python -m src.cli ai-analyze --interval 1h
python -m src.cli paper-status
python -m src.cli paper-auto --interval 1h
```

## Procedure

1. For quick signal: run `ada-signal`.
2. For full AI analysis (Thai summary + reasoning): run `ai-analyze`.
3. For paper trading: run `paper-auto`.
4. Always note that this is analysis / paper only.

## Requirements for AI Analysis

Set `OPENROUTER_API_KEY` or `OPENAI_API_KEY` in `.env`.

## Safety

No live orders. Paper trading only.
