"""
Regime_Agent — Improved Market Context Classifier
- Multi-timeframe (4h + 1h)
- EMA 20/50/200 structure on 4h
- Configurable thresholds via env
- Simple hysteresis to reduce regime flipping
"""

import os
from typing import Dict, Any, Optional
import pandas as pd

from src.data.ada_price import ADAPriceFetcher


class RegimeAgent:
    def __init__(self, source: str = "binance"):
        self.fetcher = ADAPriceFetcher(preferred_source=source)
        self._last_regime: Optional[str] = None

        # Configurable thresholds
        self.trend_threshold = float(os.getenv("REGIME_TREND_THRESHOLD", "3.5"))
        self.vol_high = float(os.getenv("REGIME_VOL_HIGH", "4.5"))
        self.range_high = float(os.getenv("REGIME_RANGE_HIGH", "2.8"))
        self.ranging_threshold = float(os.getenv("REGIME_RANGING_THRESHOLD", "1.8"))

    def classify(self, interval: str = "1h", lookback: int = 120) -> Dict[str, Any]:
        """จำแนกสภาวะตลาดปัจจุบัน (รวม 4h macro)"""
        # Fetch both timeframes
        df_1h = self.fetcher.get_with_indicators("1h", lookback)
        df_4h = self.fetcher.get_with_indicators("4h", min(lookback // 4 + 20, 100))

        if df_1h.empty or len(df_1h) < 40:
            return {"status": "error", "regime": "unknown", "message": "Not enough 1h data"}

        # 1h metrics
        close_1h = df_1h["close"]
        returns = close_1h.pct_change().dropna()
        trend_1h = (close_1h.iloc[-1] / close_1h.iloc[-min(40, len(close_1h))] - 1) * 100
        vol_pct = returns.std() * 100
        high_low_range = ((df_1h["high"] - df_1h["low"]) / close_1h).tail(15).mean() * 100

        # 4h EMA structure (macro)
        ema_bias = "neutral"
        if not df_4h.empty and len(df_4h) >= 30:
            last_4h = df_4h.iloc[-1]
            ema20 = last_4h.get("ema_20")
            ema50 = last_4h.get("ema_50")
            price_4h = last_4h["close"]

            if ema20 and ema50:
                if price_4h > ema20 > ema50:
                    ema_bias = "strong_bull"
                elif price_4h < ema20 < ema50:
                    ema_bias = "strong_bear"
                elif price_4h > ema50:
                    ema_bias = "bullish"
                elif price_4h < ema50:
                    ema_bias = "bearish"

        # Classification logic
        raw_regime = self._classify_raw(trend_1h, vol_pct, high_low_range, ema_bias)

        # Hysteresis: require stronger signal to switch away from last regime
        regime = self._apply_hysteresis(raw_regime, trend_1h, vol_pct)

        strategy_hint = self._strategy_hint(regime, ema_bias)

        self._last_regime = regime

        return {
            "status": "ok",
            "regime": regime,
            "raw_regime": raw_regime,
            "strategy_hint": strategy_hint,
            "trend_pct": round(trend_1h, 2),
            "volatility_pct": round(vol_pct, 2),
            "range_pct": round(high_low_range, 2),
            "ema_bias_4h": ema_bias,
            "interval": "1h+4h",
            "description": self._describe(regime),
        }

    def _classify_raw(self, trend: float, vol: float, range_pct: float, ema_bias: str) -> str:
        if vol > self.vol_high or range_pct > self.range_high:
            return "high_volatility"

        if abs(trend) > self.trend_threshold:
            if ema_bias in ("strong_bull", "bullish") and trend > 0:
                return "trending_bull"
            if ema_bias in ("strong_bear", "bearish") and trend < 0:
                return "trending_bear"
            return "trending_bull" if trend > 0 else "trending_bear"

        if abs(trend) < self.ranging_threshold:
            return "ranging"

        return "mixed"

    def _apply_hysteresis(self, raw: str, trend: float, vol: float) -> str:
        """ลดการสลับ regime บ่อยเกินไป"""
        if not self._last_regime or self._last_regime == raw:
            return raw

        # Require stronger evidence to leave current regime
        if self._last_regime == "trending_bull" and raw != "trending_bull":
            if trend > self.trend_threshold * 0.6:
                return "trending_bull"
        if self._last_regime == "trending_bear" and raw != "trending_bear":
            if trend < -self.trend_threshold * 0.6:
                return "trending_bear"
        if self._last_regime == "ranging" and raw != "ranging":
            if abs(trend) < self.ranging_threshold * 1.4:
                return "ranging"

        return raw

    def _strategy_hint(self, regime: str, ema_bias: str) -> str:
        if regime == "high_volatility":
            return "reduce_size_or_wait"
        if regime in ("trending_bull", "trending_bear"):
            return "trend_following"
        if regime == "ranging":
            return "mean_reversion"
        if ema_bias in ("strong_bull", "bullish"):
            return "trend_following"
        return "neutral"

    def _describe(self, regime: str) -> str:
        mapping = {
            "trending_bull": "ตลาดขึ้นแรง (Trend Following — Buy dips)",
            "trending_bear": "ตลาดลงแรง (Trend Following — Sell rallies)",
            "ranging": "ตลาดข้าง / Sideway (Mean Reversion)",
            "high_volatility": "ความผันผวนสูง — ควรลดขนาดไม้หรือรอ",
            "mixed": "สภาวะปน — ใช้กลยุทธ์ปกติ",
            "unknown": "ข้อมูลไม่เพียงพอ",
        }
        return mapping.get(regime, "ไม่ทราบ")
