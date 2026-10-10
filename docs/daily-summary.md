# Daily Summary via Telegram

## Manual
```bash
python -m src.cli daily-summary
```

## Cron (every evening at 21:00)
```bash
0 21 * * * cd /path/to/AI_trading_ADA && python -m src.cli daily-summary
```

## What is sent
- Number of trades today
- Today's P&L
- Current equity
- Whether there is an open position
- Overall stats (win rate, profit factor, max drawdown, total PnL)

## Configurable
- `SR_PROXIMITY_PCT` in `.env` controls how close price must be to support/resistance (default 1.5%)
- Each trade records `filters_passed` so you can later analyze which filters were useful
