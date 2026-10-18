"""
Gold (PAXG) Breakout Strategy

Rules:
- 4h defines Resistance 1 (max close 20 bars) and Resistance 2 (max close 40 bars)
- 1h entry: break R1 + pass wick + make high + still below R2 + volume > MA
- Stop Loss: Fixed 1.5%
- Take Profit: reach R2
- Max hold: 48 hours
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class GoldBreakoutStrategy:
    """Gold breakout strategy based on resistance levels."""

    def __init__(
        self,
        r1_lookback: int = 20,
        r2_lookback: int = 40,
        sl_pct: float = 1.5,
        max_hold_hours: int = 48,
    ):
        self.r1_lookback = r1_lookback
        self.r2_lookback = r2_lookback
        self.sl_pct = sl_pct
        self.max_hold_hours = max_hold_hours

    def calculate_resistance(self, df_4h: pd.DataFrame) -> pd.DataFrame:
        """Calculate R1 and R2 from 4h data."""
        df = df_4h.copy()
        df["r1"] = df["close"].rolling(self.r1_lookback).max().shift(1)
        df["r2"] = df["close"].rolling(self.r2_lookback).max().shift(1)
        return df[["r1", "r2"]]

    def get_signal(
        self,
        df_1h: pd.DataFrame,
        df_4h: pd.DataFrame,
    ) -> Dict[str, Any]:
        """Get current trading signal."""
        if df_1h.empty or df_4h.empty or len(df_1h) < 25 or len(df_4h) < 45:
            return {"signal": "hold", "reason": "insufficient data"}

        # Calculate resistance
        sr = self.calculate_resistance(df_4h)

        # Align to 1h
        df = df_1h.copy()
        df = df.join(sr, how="left")
        df["r1"] = df["r1"].ffill()
        df["r2"] = df["r2"].ffill()
        df["vol_ma"] = df["volume"].rolling(20).mean()
        df = df.dropna()

        if len(df) < 3:
            return {"signal": "hold", "reason": "insufficient aligned data"}

        current = df.iloc[-1]
        prev = df.iloc[-2]

        price = float(current["close"])
        high = float(current["high"])
        r1 = float(current["r1"])
        r2 = float(current["r2"])
        vol = float(current["volume"])
        vol_ma = float(current["vol_ma"])

        # Entry conditions
        cond1 = float(prev["close"]) > r1  # Break R1
        cond2 = float(prev["high"]) > r1   # Pass wick
        cond3 = high > float(prev["high"]) # Make high
        cond4 = price < r2                   # Still below R2
        cond5 = vol > vol_ma                 # Volume confirmation

        signal = "hold"
        reason = []

        if cond1 and cond2 and cond3 and cond4 and cond5:
            signal = "buy"
            reason.append("all conditions met")
        else:
            if not cond1:
                reason.append("not broken R1")
            if not cond2:
                reason.append("wick not passed")
            if not cond3:
                reason.append("no new high")
            if not cond4:
                reason.append("already at R2")
            if not cond5:
                reason.append("volume low")

        # Calculate SL and TP
        sl_price = price * (1 - self.sl_pct / 100) if signal == "buy" else None
        tp_price = r2 if signal == "buy" else None

        return {
            "signal": signal,
            "price": round(price, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "sl": round(sl_price, 2) if sl_price else None,
            "tp": round(tp_price, 2) if tp_price else None,
            "volume_ratio": round(vol / vol_ma, 2) if vol_ma > 0 else 0,
            "reason": ", ".join(reason),
        }
