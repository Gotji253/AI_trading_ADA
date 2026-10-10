# Hermes Learning from Paper Trades

## Quick Way

1. Make sure you have some paper trades:
   ```bash
   python -m src.cli paper-auto
   python -m src.cli memory
   ```

2. In Hermes, use the new skill:
   ```
   /ada-learn
   ```
   Or simply say:
   "อ่านผลการเทรด paper แล้วเสนอปรับปรุงกลยุทธ์ หรือสร้าง skill ใหม่"

3. Hermes will:
   - Read `data/trade_memory.json`
   - Suggest concrete parameter changes
   - Optionally create a new skill that captures a winning pattern

## Generate a ready prompt

```bash
python -m src.memory.learning_prompt
```

Copy the output and paste it into Hermes if you want to force the learning step.

## What Hermes can change / suggest

- Confidence threshold (currently 0.4 in paper trader)
- `MAX_POSITION_PCT`
- Whether to require multi-timeframe agreement
- New entry rules (e.g. only buy near support)

## Safety

All suggestions are for **paper mode**.  
Never apply changes to live trading without explicit confirmation.
