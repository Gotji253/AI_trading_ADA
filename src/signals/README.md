# ADA Signal Generator

## Usage

```python
from src.signals.ada_signals import ADASignalGenerator

gen = ADASignalGenerator(source="binance")
result = gen.generate(interval="1h")
print(result)
```

## Logic (current)

- RSI < 30 → buy bias
- RSI > 70 → sell bias
- Price > EMA20 > EMA50 → uptrend buy
- Price < EMA20 < EMA50 → downtrend sell
- MACD bullish/bearish crossover

Stop-loss / Take-profit based on approximate ATR.
