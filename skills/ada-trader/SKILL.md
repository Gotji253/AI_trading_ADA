# ADA Trader Skill

Specialized skill for Hermes Agent to analyze and propose trades **exclusively for Cardano (ADA)**.

## Trigger

Invoke with `/ada-trader` or natural language requests about ADA trading.

## Capabilities

1. **Market Snapshot**
   - Fetch current ADA/USDT price, 24h volume, change %
   - Technical indicators: RSI(14), MACD, EMA 20/50/200, Bollinger Bands

2. **Signal Generation**
   - Bullish / Bearish / Neutral
   - Entry, Stop-Loss, Take-Profit levels
   - Position sizing suggestion based on risk %

3. **Risk Checks**
   - Volatility filter
   - Max drawdown awareness
   - No trades outside ADA

4. **Output Format**
   Always respond in structured form (JSON preferred for automation) + Thai summary.

## Example Invocation

```
/ada-trader analyze today
```

## Implementation Notes

- Use tools for real-time data (CCXT, Binance API, or free sources).
- Store past signals and outcomes in Hermes memory for learning.
- Paper trading mode by default.

## Safety Rules

- Refuse any request to trade other coins.
- Require confirmation before any live order.
- Log every decision.
