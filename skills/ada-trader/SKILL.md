---
name: ada-trader
description: Analyze ADA and run paper trading. Generate signals and simulate trades. Use for ADA analysis or paper trading status.
version: 1.2.0
author: AI_trading_ADA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ADA, Cardano, Trading, Paper, Signals]
    category: finance
    requires_toolsets: [terminal]
---

# ADA Trader Skill (with Paper Trading)

ADA only. Paper trading by default.

## Commands (via terminal)

```bash
python -m src.cli status
python -m src.cli ada-signal --interval 1h
python -m src.cli paper-status
python -m src.cli paper-auto --interval 1h
python -m src.cli paper-history
```

## Procedure

1. For analysis: run `ada-signal`.
2. For paper trading: run `paper-auto` (it will open/close virtual positions based on the signal).
3. Check account with `paper-status`.
4. Always state that this is paper trading — no real money.

## Safety

- Never place real orders.
- Paper state is stored locally in `data/paper_state.json`.
