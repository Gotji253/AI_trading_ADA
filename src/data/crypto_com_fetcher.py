"""
Crypto.com Price Data Fetcher for ADA
Alternative data source when Binance is geo-restricted.
"""

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import requests
import pandas as pd


class CryptoComFetcher:
    """Fetch ADA/USDT data from Crypto.com Exchange public API."""

    BASE = "https://api.crypto.com/exchange/v1/public"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AI_trading_ADA/1.0"})

    def get_ohlcv(self, interval: str = "1h", limit: int = 50) -> pd.DataFrame:
        """
        Get OHLCV candles from Crypto.com.
        Note: Public API returns limited recent candles.
        """
        # Map interval
        tf_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "4h": "4h", "1d": "1D"
        }
        timeframe = tf_map.get(interval, "1h")

        url = f"{self.BASE}/get-candlestick"
        params = {
            "instrument_name": "ADA_USDT",
            "timeframe": timeframe,
        }

        try:
            r = self.session.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()

            candles = data.get("result", {}).get("data", [])
            if not candles:
                return pd.DataFrame()

            rows = []
            for c in candles[:limit]:
                rows.append({
                    "timestamp": pd.to_datetime(c.get("t", c.get("timestamp")), unit="ms", utc=True),
                    "open": float(c.get("o", c.get("open", 0))),
                    "high": float(c.get("h", c.get("high", 0))),
                    "low": float(c.get("l", c.get("low", 0))),
                    "close": float(c.get("c", c.get("close", 0))),
                    "volume": float(c.get("v", c.get("volume", 0))),
                })

            df = pd.DataFrame(rows)
            if df.empty:
                return df
            df = df.set_index("timestamp").sort_index()
            return df[["open", "high", "low", "close", "volume"]]

        except Exception as e:
            print(f"Crypto.com fetch error: {e}")
            return pd.DataFrame()

    def get_with_indicators(self, interval: str = "1h", limit: int = 50) -> pd.DataFrame:
        df = self.get_ohlcv(interval, limit)
        if df.empty:
            return df
        close = df["close"]
        df["ema_20"] = close.ewm(span=min(20, len(df)), adjust=False).mean()
        df["ema_50"] = close.ewm(span=min(50, len(df)), adjust=False).mean()
        return df


def main():
    f = CryptoComFetcher()
    df = f.get_ohlcv("1h", 30)
    print(f"Candles: {len(df)}")
    if not df.empty:
        print(df.tail(3))


if __name__ == "__main__":
    main()
