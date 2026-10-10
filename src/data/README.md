# ADA Price Data Module

## Usage

```python
from src.data.ada_price import ADAPriceFetcher

fetcher = ADAPriceFetcher(preferred_source="binance")  # or "coingecko"

# Current price
print(fetcher.get_current_price())

# OHLCV + indicators
df = fetcher.get_with_indicators(interval="1h", limit=100)
print(df.tail())
```

## Sources
- **Binance** (recommended): real OHLCV, no key needed for public data
- **CoinGecko**: free, simpler, limited historical OHLC on free tier

## Notes
- For Hermes skill: import and call `get_current_price()` or `get_with_indicators()`
- Rate limits: Binance is generous for public endpoints; CoinGecko free has limits
