"""
Regime_Agent — Market Context Classifier
จำแนกสภาวะตลาด ADA: Trending (Bull/Bear), Ranging, High Volatility
"""

from typing import Dict, Any
import pandas as pd

from src.data.ada_price import ADAPriceFetcher


class RegimeAgent:
    def __init__(self, source: str = "binance"):
        self.fetcher = ADAPriceFetcher(preferred_source=source)

    def classify(self, interval: str = "1h", lookback: int = 100) -> Dict[str, Any]:
        """จำแนกสภาวะตลาดปัจจุบัน"""
        df = self.fetcher.get_with_indicators(interval, lookback)
        if df.empty or len(df) < 30:
            return {"status": "error", "regime": "unknown", "message": "Not enough data"}

        close = df["close"]
        returns = close.pct_change().dropna()

        # Trend strength (price change over window)
        trend_pct = (close.iloc[-1] / close.iloc[-min(50, len(close))] - 1) * 100

        # Volatility (std of returns)
        vol_pct = returns.std() * 100

        # ATR-like range
        high_low_range = ((df["high"] - df["low"]) / close).tail(20).mean() * 100

        # Classification
        if abs(trend_pct) > 4 and vol_pct < 3:
            regime = "trending_bull" if trend_pct > 0 else "trending_bear"
            strategy_hint = "trend_following"
        elif vol_pct > 5 or high_low_range > 3:
            regime = "high_volatility"
            strategy_hint = "reduce_size_or_wait"
        elif abs(trend_pct) < 2:
            regime = "ranging"
            strategy_hint = "mean_reversion"
        else:
            regime = "mixed"
            strategy_hint = "neutral"

        return {
            "status": "ok",
            "regime": regime,
            "strategy_hint": strategy_hint,
            "trend_pct": round(trend_pct, 2),
            "volatility_pct": round(vol_pct, 2),
            "range_pct": round(high_low_range, 2),
            "interval": interval,
            "description": self._describe(regime),
        }

    def _describe(self, regime: str) -> str:
        mapping = {
            "trending_bull": "ตลาดขึ้นแรง เหมาะกับ Trend Following (Buy dips)",
            "trending_bear": "ตลาดลงแรง เหมาะกับ Trend Following (Sell rallies)",
            "ranging": "ตลาดข้าง (Sideway) เหมาะกับ Mean Reversion",
            "high_volatility": "ความผันผวนสูง ควรลดขนาดไม้หรือรอ",
            "mixed": "สภาวะปน ใช้กลยุทธ์ปกติ",
            "unknown": "ข้อมูลไม่เพียงพอ",
        }
        return mapping.get(regime, "ไม่ทราบ")
