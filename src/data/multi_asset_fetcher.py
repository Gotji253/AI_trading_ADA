"""
Multi-Asset Price Fetcher
Supports BTC, ETH, SOL, BNB, XRP
"""

import os
import requests
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime

from src.config.assets import get_trading_assets, get_asset_info


class MultiAssetFetcher:
    """Fetch OHLCV data for multiple assets."""

    def __init__(self):
        self.assets = get_trading_assets()
        self.binance_base = "https://api.binance.com"
        self.crypto_com_base = "https://api.crypto.com/v2/public"

    def get_ohlcv(self, symbol: str, interval: str = "1h", limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV for a single asset."""
        # Try Binance first
        df = self._binance_klines(symbol, interval, limit)
        if df is not None and not df.empty:
            return df

        # Fallback to Crypto.com
        return self._crypto_com_candlestick(symbol, interval, limit)

    def get_all_prices(self) -> Dict[str, float]:
        """Get current prices for all trading assets."""
        prices = {}
        for symbol in self.assets:
            df = self.get_ohlcv(symbol, "1h", 1)
            if df is not None and not df.empty:
                prices[symbol] = float(df["close"].iloc[-1])
        return prices

    def get_multi_asset_data(self, interval: str = "1h", limit: int = 100) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV for all trading assets."""
        data = {}
        for symbol in self.assets:
            df = self.get_ohlcv(symbol, interval, limit)
            if df is not None and not df.empty:
                data[symbol] = df
        return data

    def _binance_klines(self, symbol: str, interval: str, limit: int) -> Optional[pd.DataFrame]:
        try:
            url = f"{self.binance_base}/api/v3/klines"
            params = {"symbol": symbol, "interval": interval, "limit": limit}
            headers = {}
            api_key = os.getenv("BINANCE_API_KEY", "").strip()
            if api_key:
                headers["X-MBX-APIKEY"] = api_key

            r = requests.get(url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            if not data:
                return None

            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ])
            df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")
            df = df.set_index("timestamp")
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            return df[["open", "high", "low", "close", "volume"]]
        except Exception:
            return None

    def _crypto_com_candlestick(self, symbol: str, interval: str, limit: int) -> Optional[pd.DataFrame]:
        try:
            # Convert symbol format: BTCUSDT -> BTC_USDT
            cc_symbol = symbol.replace("USDT", "_USDT")
            url = f"{self.crypto_com_base}/get-candlestick"
            params = {"instrument_name": cc_symbol, "timeframe": interval}
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()

            if data.get("code") != 0:
                return None

            candles = data.get("result", {}).get("data", [])
            if not candles:
                return None

            df = pd.DataFrame(candles)
            df["timestamp"] = pd.to_datetime(df["t"], unit="ms")
            df = df.set_index("timestamp").sort_index()
            df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            return df[["open", "high", "low", "close", "volume"]].tail(limit)
        except Exception:
            return None


def main():
    fetcher = MultiAssetFetcher()
    print(f"Trading assets: {fetcher.assets}")
    prices = fetcher.get_all_prices()
    for sym, price in prices.items():
        info = get_asset_info(sym)
        print(f"{info['name']}: ${price:,.2f}")


if __name__ == "__main__":
    main()
