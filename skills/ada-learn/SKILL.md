---
name: ada-learn
description: Review paper trading memory and suggest parameter changes or create a new skill based on profitable patterns. Use when asked to learn from past trades or improve the ADA strategy.
version: 1.0.0
author: AI_trading_ADA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ADA, Learning, Memory, Skill-Creation]
    category: finance
    requires_toolsets: [terminal, filesystem]
---

# ADA Learning Skill

Use this skill when the user wants Hermes to learn from paper trading results.

## When to Use

- "วิเคราะห์ผลการเทรดที่ผ่านมา"
- "ปรับปรุงกลยุทธ์จาก memory"
- "สร้าง skill ใหม่จากรูปแบบที่ทำกำไร"

## Procedure

1. Read the memory file with the terminal tool:
   ```bash
   python -m src.cli memory
   ```
   Or directly:
   ```bash
   cat data/trade_memory.json
   ```

2. Analyze the content:
   - Look at `stats` (win_rate, profit_factor, max_drawdown_pct, total_pnl)
   - Look at `recent_trades`
   - Read the `lessons` array

3. Based on the data, do one or both of the following:

   **A. Suggest parameter changes** (reply in Thai):
   - If win rate is low → suggest raising confidence threshold or requiring multi-tf agreement
   - If drawdown is high → suggest reducing MAX_POSITION_PCT or tighter stop-loss
   - If profit factor < 1 → suggest pausing auto-trade or adding more filters
   - Give concrete numbers (e.g. "ลองเปลี่ยน confidence จาก 0.4 เป็น 0.55")

   **B. Create a new skill** (if there is a clear winning pattern):
   - Write a new SKILL.md under `~/.hermes/skills/finance/ada-pattern-xxx/SKILL.md`
   - The new skill should describe the observed profitable condition (e.g. "buy only when 1h and 4h both buy and RSI < 40")
   - Keep it short and actionable

4. Always end with a short Thai summary of what you recommend and whether you created a new skill.

## Safety

- Do not change live trading settings.
- Suggestions are for paper mode only.
- Ask the user before applying any parameter change permanently.
