# Deeper Hermes Integration Notes

## 1. Hourly Cron Job

In Hermes you can schedule:

```
/cron add "every hour" python -m src.scheduler.hourly
```

Or use system cron:

```bash
0 * * * * cd /path/to/AI_trading_ADA && python -m src.scheduler.hourly >> logs/hourly.log
```

The script outputs a JSON report with multi-tf, levels, news, on-chain tip, and memory update.

## 2. Memory of Paper Trades

- File: `data/trade_memory.json`
- Updated automatically when you run hourly analysis or `python -m src.memory.trade_memory`
- Feed the `lessons` and `stats` into AI analysis prompts so the agent learns from past paper results.

## 3. Self-Improving Skills (Hermes native)

Hermes can create new skills from experience. Suggested workflow:

1. After several profitable paper trades, ask Hermes:
   "Review the last 10 paper trades in data/trade_memory.json and create a new skill that captures the winning pattern."
2. Hermes will write a new SKILL.md under ~/.hermes/skills/
3. Review and keep only useful skills.

## 4. Notification

Extend `src/scheduler/hourly.py` to send Telegram / Discord message using the `alert` field.
You can add a simple requests call if you set TELEGRAM_BOT_TOKEN and CHAT_ID in .env.
