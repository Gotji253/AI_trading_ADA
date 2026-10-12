"""
Enhanced Market Analyzer - Extremely Flexible Criteria
"""

import os
from typing import Dict, Any, Optional
import pandas as pd


class EnhancedAnalyzer:
    """Extremely flexible analyzer."""

    def __init__(self):
        self.sr_proximity = float(os.getenv("SR_PROXIMITY_PCT", "4.0"))
        self.volume_mult = float(os.getenv("VOLUME_MULTIPLIER", "0.5"))
        self.min_tf_agreement = int(os.getenv("MIN_TF_AGREEMENT", "1"))

    def analyze(self, df_1h: pd.DataFrame, df_4h: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        if df_1h is None or len(df_1h) < 15:
            return {"status": "error", "message": "Insufficient data"}

        price = float(df_1h["close"].iloc[-1])

        tf_signals = {}
        tf_signals["1h"] = self._tf_signal(df_1h)
        if df_4h is None or len(df_4h) < 5:
            df_4h = self._resample(df_1h, "4h")
        tf_signals["4h"] = self._tf_signal(df_4h)

        bullish_count = sum(1 for s in tf_signals.values() if s.get("bias") == "bullish")
        bearish_count = sum(1 for s in tf_signals.values() if s.get("bias") == "bearish")
        agreement = max(bullish_count, bearish_count)

        volume_ok = self._volume_confirmation(df_1h)
        levels = self._find_levels(df_1h)
        near_support = self._near_level(price, levels.get("support"))
        near_resistance = self._near_level(price, levels.get("resistance"))
        rsi = self._rsi(df_1h["close"])
        regime = self._classify_regime(df_1h)

        signal = "hold"
        setup_type = None
        quality = "none"
        multi_tf_ok = agreement >= self.min_tf_agreement

        # Extremely flexible
        if near_support and rsi < 55 and volume_ok and multi_tf_ok and regime != "trending_bear":
            signal = "buy"
            setup_type = "pullback_to_support"
            quality = "high"
        elif near_resistance and rsi > 45 and volume_ok and multi_tf_ok and regime != "trending_bull":
            signal = "sell"
            setup_type = "rally_to_resistance"
            quality = "high"

        return {
            "status": "ok",
            "signal": signal,
            "setup_type": setup_type,
            "quality": quality,
            "price": price,
            "rsi": round(rsi, 1),
            "regime": regime,
            "volume_confirmed": volume_ok,
            "multi_tf_agreement": agreement,
            "near_support": near_support,
            "near_resistance": near_resistance,
            "levels": levels,
        }

    def _tf_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        if len(df) < 5:
            return {"bias": "neutral"}
        close = df["close"]
        ema = close.ewm(span=min(8, len(df)), adjust=False).mean().iloc[-1]
        price = float(close.iloc[-1])
        return {"bias": "bullish" if price > ema else "bearish"}

    def _volume_confirmation(self, df: pd.DataFrame) -> bool:
        if "volume" not in df.columns or len(df) < 8:
            return True
        current = float(df["volume"].iloc[-1])
        avg = float(df["volume"].tail(8).mean())
        return current >= avg * self.volume_mult

    def _find_levels(self, df: pd.DataFrame) -> Dict[str, float]:
        recent = df.tail(15)
        return {"support": float(recent["low"].min()), "resistance": float(recent["high"].max())}

    def _near_level(self, price: float, level: Optional[float]) -> bool:
        if not level or level <= 0:
            return False
        return abs(price - level) / level * 100 <= self.sr_proximity

    def _rsi(self, series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if len(rsi) > 0 else 50.0

    def _classify_regime(self, df: pd.DataFrame) -> str:
        if len(df) < 8:
            return "unknown"
        close = df["close"]
        trend = (float(close.iloc[-1]) / float(close.iloc[-8]) - 1) * 100
        if trend > 2:
            return "trending_bull"
        elif trend < -2:
            return "trending_bear"
        return "mixed"

    def _resample(self, df: pd.DataFrame, rule: str) -> pd.DataFrame:
        try:
            return df.resample(rule).agg({
                "open": "first", "high": "max", "low": "min",
                "close": "last", "volume": "sum"
            }).dropna()
        except Exception:
            return pd.DataFrame()
