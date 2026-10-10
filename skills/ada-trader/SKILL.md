# ADA Trader Skill (Hermes)

Specialized skill for Hermes Agent — **ADA only**.

## Trigger

`/ada-trader` or natural language about ADA trading / analysis.

## How to use in Hermes

1. Copy `src/` into your Hermes workspace or add it to PYTHONPATH.
2. The skill should call the Python modules below.

## Recommended implementation (for Hermes tool / skill)

```python
from src.signals.ada_signals import ADASignalGenerator

gen = ADASignalGenerator(source="binance")
result = gen.generate(interval="1h")
# Return result as JSON + Thai summary
```

## Output fields

- `signal`: buy | sell | hold
- `confidence`: 0.0 – 1.0
- `price`, `rsi`, `ema20`, `ema50`
- `stop_loss`, `take_profit`
- `reasons`: list of why the signal was generated

## Safety

- ADA only. Refuse other coins.
- Paper / dry-run by default.
- Require explicit user confirmation before any live order.

## Example Thai summary

"ADA ปัจจุบันราคา X USDT, RSI Y, สัญญาณ: ซื้อ/ขาย/ถือ (ความมั่นใจ Z%)"
