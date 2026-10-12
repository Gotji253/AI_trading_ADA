"""
Regime_Agent — Enhanced Market Context Classifier
- Multi-timeframe (4h + 1h)
- EMA 20/50/200 structure on 4h
- ATR-based volatility
- Volume confirmation
- Confidence score
- Configurable thresholds + hysteresis
"""

import os
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from src.data.ada_price import ADAPriceFetcher


class RegimeAgent:
    def __init__(self, source: str = "binance"):
        self.fetcher = ADAPriceFetcher(preferred_source=source)
        self._last_regime: Optional[str] = None

        self.trend_threshold = float(os.getenv("REGIME_TREND_THRESHOLD", "3.5"))
        self.vol_high = float(os.getenv("REGIME_VOL_HIGH", "4.5"))
        self.ranging_threshold = float(os.getenv("REGIME_RANGING_THRESHOLD", "1.8"))

    def classify(self, interval: str = "1h", lookback: int = 150) -> Dict[str, Any]:
        df_1h = self.fetcher.get_with_indicators("1h", lookback)
        df_4h = self.fetcher.get_with_indicators("4h", 80)

        if df_1h.empty or len(df_1h) < 50:
            return {"status": "error", "regime": "unknown", "message": "Not enough data"}

        # --- 1h metrics ---
        close = df_1h["close"]
        returns = close.pct_change().dropna()
        trend_pct = (close.iloc[-1] / close.iloc[-40] - 1) * 100
        vol_pct = returns.std() * 100

        # ATR (14)
        atr = self._atr(df_1h, 14)
        atr_pct = (atr / close.iloc[-1] * 100) if atr and close.iloc[-1] else 0

        # Volume confirmation (last 5 vs previous 20)
        vol_ratio = self._volume_ratio(df_1h)

        # --- 4h EMA structure ---
        ema_bias = "neutral"
        ema200_ok = False
        if not df_4h.empty and len(df_4h) >= 40:
            last = df_4h.iloc[-1]
            p = last["close"]
            e20 = last.get("ema_20")
            e50 = last.get("ema_50")
            # Approximate EMA200 if not present
            e200 = last.get("ema_200") or df_4h["close"].ewm(span=200, adjust=False).mean().iloc[-1]

            if e20 and e50:
                if p > e20 > e50 > e200:
                    ema_bias = "strong_bull"
                    ema200_ok = True
                elif p < e20 < e50 < e200:
                    ema_bias = "strong_bear"
                    ema200_ok = True
                elif p > e50:
                    ema_bias = "bullish"
                elif p < e50:
                    ema_bias = "bearish"

        # Classification
        raw = self._classify(trend_pct, vol_pct, atr_pct, ema_bias, vol_ratio)
        regime = self._hysteresis(raw, trend_pct)
        confidence = self._confidence(regime, trend_pct, vol_pct, atr_pct, ema_bias, vol_ratio)
        hint = self._hint(regime, ema_bias)

        self._last_regime = regime

        return {
            "status": "ok",
            "regime": regime,
            "raw_regime": raw,
            "confidence": round(confidence, 2),
            "strategy_hint": hint,
            "trend_pct": round(trend_pct, 2),
            "volatility_pct": round(vol_pct, 2),
            "atr_pct": round(atr_pct, 2),
            "volume_ratio": round(vol_ratio, 2),
            "ema_bias_4h": ema_bias,
            "ema200_aligned": ema200_ok,
            "description": self._describe(regime),
        }

    def _atr(self, df: pd.DataFrame, period: int = 14) -> float:
        if len(df) < period + 1:
            return 0.0
        high, low, close = df["high"], df["low"], df["close"]
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        return float(tr.rolling(period).mean().iloc[-1])

    def _volume_ratio(self, df: pd.DataFrame) -> float:
        if "volume" not in df.columns or len(df) < 25:
            return 1.0
        recent = df["volume"].tail(5).mean()
        older = df["volume"].iloc[-25:-5].mean()
        return float(recent / older) if older > 0 else 1.0

    def _classify(self, trend: float, vol: float, atr_pct: float, ema: str, vol_ratio: float) -> str:
        if vol > self.vol_high or atr_pct > 2.5:
            return "high_volatility"

        strong_trend = abs(trend) > self.trend_threshold
        if strong_trend:
            if ema in ("strong_bull", "bullish") and trend > 0 and vol_ratio > 0.8:
                return "trending_bull"
            if ema in ("strong_bear", "bearish") and trend < 0 and vol_ratio > 0.8:
                return "trending_bear"
            return "trending_bull" if trend > 0 else "trending_bear"

        if abs(trend) < self.ranging_threshold:
            return "ranging"

        return "mixed"

    def _hysteresis(self, raw: str, trend: float) -> str:
        if not self._last_regime or self._last_regime == raw:
            return raw
        if self._last_regime == "trending_bull" and trend > self.trend_threshold * 0.55:
            return "trending_bull"
        if self._last_regime == "trending_bear" and trend < -self.trend_threshold * 0.55:
            return "trending_bear"
        if self._last_regime == "ranging" and abs(trend) < self.ranging_threshold * 1.5:
            return "ranging"
        return raw

    def _confidence(self, regime: str, trend: float, vol: float, atr_pct: float, ema: str, vol_ratio: float) -> float:
        base = 0.4
        if regime in ("trending_bull", "trending_bear"):
            base += min(abs(trend) / 10, 0.3)
            if ema.startswith("strong"):
                base += 0.2
            if vol_ratio > 1.1:
                base += 0.1
        elif regime == "ranging":
            base += 0.25 if abs(trend) < 1.0 else 0.1
        elif regime == "high_volatility":
            base += min(atr_pct / 5, 0.3)
        return min(base, 0.95)

    def _hint(self, regime: str, ema: str) -> str:
        if regime == "high_volatility":
            return "reduce_size_or_wait"
        if regime in ("trending_bull", "trending_bear"):
            return "trend_following"
        if regime == "ranging":
            return "mean_reversion"
        return "neutral"

    def _describe(self, regime: str) -> str:
        m = {
            "trending_bull": "ตลาดขึ้นแรง — Trend Following (Buy dips)",
            "trending_bear": "ตลาดลงแรง — Trend Following (Sell rallies)",
            "ranging": "ตลาดข้าง — Mean Reversion",
            "high_volatility": "ความผันผวนสูง — ลดขนาดไม้หรือรอ",
            "mixed": "สภาวะปน",
            "unknown": "ข้อมูลไม่พอ",
        }
        return m.get(regime, "ไม่ทราบ")
