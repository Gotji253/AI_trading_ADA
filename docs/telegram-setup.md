# Telegram Notification Setup

## 1. Create Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the **Bot Token**

## 2. Get Chat ID
1. Send any message to your new bot
2. Open this URL in browser (replace TOKEN):
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. Find `"chat":{"id":123456789}` → that number is your `TELEGRAM_CHAT_ID`

## 3. Configure
Add to `.env`:
```
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
```

## 4. Test
```bash
python -m src.notify.telegram
```

## What gets notified
- Hourly analysis report (`python -m src.cli hourly`)
- Paper trade open / close (including SL/TP)

## Cron example (hourly)
```bash
0 * * * * cd /path/to/AI_trading_ADA && python -m src.cli hourly
```
