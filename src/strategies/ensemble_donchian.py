"""
Ensemble Donchian + ADX + Vol Filter Strategy

Entry: ≥2 Donchian periods breakout AND ADX > 25 AND Vol not Q4
Exit: ≥2 Donchian periods breakdown
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List


class EnsembleDonchianStrategy:
    """Ensemble Donchian with ADX and Vol filters."""

    def __init__(
        self,
        periods: List[int] = None,
        min_agree: int = 2,
        adx_threshold: float = 25.0,
        skip_vol_regimes: List[str] = None,
    ):
        self.periods = periods or [5, 10, 20, 30]
        self.min_agree = min_agree
        self.adx_threshold = adx_threshold
        self.skip_vol_regimes = skip_vol_regimes or ["Q4"]

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required indicators."""
        df = df.copy()

        # True Range
        df["tr"] = np.maximum(
            df["high"] - df["low"],
            np.maximum(
                abs(df["high"] - df["close"].shift(1)),
                abs(df["low"] - df["close"].shift(1))
            )
        )

        # ADX
        period = 14
        df["up_move"] = df["high"] - df["high"].shift(1)
        df["down_move"] = df["low"].shift(1) - df["low"]
        df["plus_dm"] = np.where(
            (df["up_move"] > df["down_move"]) & (df["up_move"] > 0), df["up_move"], 0
        )
        df["minus_dm"] = np.where(
            (df["down_move"] > df["up_move"]) & (df["down_move"] > 0), df["down_move"], 0
        )

        df["atr"] = df["tr"].rolling(period).mean()
        df["plus_di"] = 100 * (df["plus_dm"].rolling(period).mean() / df["atr"])
        df["minus_di"] = 100 * (df["minus_dm"].rolling(period).mean() / df["atr"])
        df["dx"] = 100 * abs(df["plus_di"] - df["minus_di"]) / (df["plus_di"] + df["minus_di"])
        df["adx"] = df["dx"].rolling(period).mean()

        # Vol Regime
        df["atr_pct"] = df["atr"] / df["close"] * 100
        valid = df["atr_pct"].dropna()
        if len(valid) >= 4:
            df["vol_regime"] = pd.qcut(
                df["atr_pct"], 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop"
            )
        else:
            df["vol_regime"] = "Q2"

        # Donchian Channels
        for p in self.periods:
            df[f"don_high_{p}"] = df["high"].rolling(p).max().shift(1)
            df[f"don_low_{p}"] = df["low"].rolling(p).min().shift(1)

        return df

    def get_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get current trading signal."""
        df = self.calculate_indicators(df)

        if df.empty or len(df) < 30:
            return {"signal": "hold", "reason": "insufficient data"}

        current = df.iloc[-1]
        price = float(current["close"])
        adx = float(current["adx"]) if pd.notna(current["adx"]) else 0
        regime = str(current["vol_regime"]) if pd.notna(current["vol_regime"]) else "Q2"

        # Count breakouts/breakdowns
        breakout_count = sum(
            1 for p in self.periods
            if pd.notna(current.get(f"don_high_{p}")) and price > current[f"don_high_{p}"]
        )
        breakdown_count = sum(
            1 for p in self.periods
            if pd.notna(current.get(f"don_low_{p}")) and price < current[f"don_low_{p}"]
        )

        # Check filters
        adx_pass = adx >= self.adx_threshold
        vol_pass = regime not in self.skip_vol_regimes

        signal = "hold"
        reason = []

        if breakout_count >= self.min_agree:
            if adx_pass and vol_pass:
                signal = "buy"
                reason.append(f"breakout {breakout_count}/{len(self.periods)}")
            else:
                if not adx_pass:
                    reason.append(f"ADX {adx:.1f} < {self.adx_threshold}")
                if not vol_pass:
                    reason.append(f"Vol regime {regime} skipped")
        elif breakdown_count >= self.min_agree:
            signal = "sell"
            reason.append(f"breakdown {breakdown_count}/{len(self.periods)}")

        return {
            "signal": signal,
            "price": price,
            "adx": round(adx, 1),
            "vol_regime": regime,
            "breakout_count": breakout_count,
            "breakdown_count": breakdown_count,
            "adx_pass": adx_pass,
            "vol_pass": vol_pass,
            "reason": ", ".join(reason) if reason else "no signal",
        }

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Full analysis with all indicators."""
        signal = self.get_signal(df)
        df = self.calculate_indicators(df)

        if df.empty:
            return {"status": "error", "message": "no data"}

        current = df.iloc[-1]

        return {
            "status": "ok",
            **signal,
            "atr": round(float(current["atr"]), 2) if pd.notna(current["atr"]) else None,
            "atr_pct": round(float(current["atr_pct"]), 2) if pd.notna(current["atr_pct"]) else None,
        }
