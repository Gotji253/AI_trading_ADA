"""
ADA Price Data Fetcher
Supports CoinGecko (free, no key) and Binance (optional API key).
Used by Hermes Agent ADA trading skill.
"""

import os
import time
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

import requests
import pandas as pd


class ADAPriceFetcher:
    """Fetch ADA/USDT price data and basic technicals."""

    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    BINANCE_BASE = "https://api.binance.com/api/v3"

    def __init__(self, preferred_source: str = "coingecko"):
        self.preferred_source = preferred_source.lower()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AI_trading_ADA/1.0"})

        # Binance API keys (optional)
        self.binance_api_key = os.getenv("BINANCE_API_KEY", "")
        self.binance_api_secret = os.getenv("BINANCE_API_SECRET", "")

    def get_current_price(self) -> Dict[str, Any]:
        """Get current ADA price snapshot."""
        if self.preferred_source == "binance":
            return self._binance_ticker()
        return self._coingecko_price()

    def get_ohlcv(
        self,
        interval: str = "1h",
        limit: int = 200,
        source: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get OHLCV candles for ADA.
        interval: 1m, 5m, 15m, 1h, 4h, 1d
        """
        src = (source or self.preferred_source).lower()
        if src == "binance":
            return self._binance_klines(interval, limit)
        return self._coingecko_ohlc(interval, limit)

    def get_with_indicators(self, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
        """OHLCV + RSI, EMA, MACD."""
        df = self.get_ohlcv(interval, limit)
        if df.empty:
            return df
        df = self._add_indicators(df)
        return df

    def _binance_headers(self) -> Dict[str, str]:
        headers = {}
        if self.binance_api_key:
            headers["X-MBX-APIKEY"] = self.binance_api_key
        return headers

    # ---------- CoinGecko ----------
    def _coingecko_price(self) -> Dict[str, Any]:
        url = f"{self.COINGECKO_BASE}/simple/price"
        params = {
            "ids": "cardano",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        r = self.session.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()["cardano"]
        return {
            "symbol": "ADA",
            "price_usd": data["usd"],
            "change_24h_pct": data.get("usd_24h_change"),
            "volume_24h_usd": data.get("usd_24h_vol"),
            "market_cap_usd": data.get("usd_market_cap"),
            "source": "coingecko",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _coingecko_ohlc(self, interval: str, limit: int) -> pd.DataFrame:
        days = max(1, limit // 24) if interval == "1h" else 30
        url = f"{self.COINGECKO_BASE}/coins/cardano/market_chart"
        params = {"vs_currency": "usd", "days": str(days)}
        r = self.session.get(url, params=params, timeout=20)
        r.raise_for_status()
        prices = r.json().get("prices", [])
        if not prices:
            return pd.DataFrame()

        df = pd.DataFrame(prices, columns=["timestamp_ms", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)
        df = df.set_index("timestamp")[["close"]]
        df["open"] = df["close"].shift(1)
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["volume"] = 0.0
        df = df.dropna().tail(limit)
        return df[["open", "high", "low", "close", "volume"]]

    # ---------- Binance ----------
    def _binance_ticker(self) -> Dict[str, Any]:
        url = f"{self.BINANCE_BASE}/ticker/24hr"
        params = {"symbol": "ADAUSDT"}
        r = self.session.get(url, params=params, headers=self._binance_headers(), timeout=15)
        r.raise_for_status()
        data = r.json()
        return {
            "symbol": "ADA",
            "price_usd": float(data["lastPrice"]),
            "change_24h_pct": float(data["priceChangePercent"]),
            "volume_24h_usd": float(data["quoteVolume"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "source": "binance",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _binance_klines(self, interval: str, limit: int) -> pd.DataFrame:
        url = f"{self.BINANCE_BASE}/klines"
        params = {"symbol": "ADAUSDT", "interval": interval, "limit": min(limit, 1000)}
        r = self.session.get(url, params=params, headers=self._binance_headers(), timeout=20)
        r.raise_for_status()
        raw = r.json()
        if not raw:
            return pd.DataFrame()

        cols = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_base",
            "taker_buy_quote", "ignore",
        ]
        df = pd.DataFrame(raw, columns=cols)
        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        df = df.set_index("timestamp")
        for c in ["open", "high", "low", "close", "volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df[["open", "high", "low", "close", "volume"]]

    # ---------- Indicators ----------
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        df["ema_50"] = close.ewm(span=50, adjust=False).mean()
        df["rsi_14"] = self._rsi(close, 14)
        df["macd"], df["macd_signal"], df["macd_hist"] = self._macd(close)
        return df

    @staticmethod
    def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist


def main():
    """Quick CLI test."""
    fetcher = ADAPriceFetcher(preferred_source="binance")
    print("=== Current ADA Price ===")
    print(fetcher.get_current_price())
    print("\n=== Latest candles with indicators (1h) ===")
    df = fetcher.get_with_indicators("1h", 30)
    if not df.empty:
        print(df.tail(5).to_string())
    else:
        print("No data")


if __name__ == "__main__":
    main()
