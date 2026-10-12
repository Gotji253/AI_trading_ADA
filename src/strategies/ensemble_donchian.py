"""
Ensemble Donchian + ADX + Vol Filter + BTC Trend Filter Strategy
Improved version: Limited to BTC/ETH/BNB, BTC SMA50>SMA200, min hold 7 days
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List


class EnsembleDonchianStrategy:
    """Improved Ensemble Donchian strategy."""

    def __init__(
        self,
        periods: List[int] = None,
        min_agree: int = 2,
        adx_threshold: float = 25.0,
        skip_vol_regimes: List[str] = None,
        min_hold_days: int = 7,
        use_btc_trend_filter: bool = True,
    ):
        self.periods = periods or [5, 10, 20, 30]
        self.min_agree = min_agree
        self.adx_threshold = adx_threshold
        self.skip_vol_regimes = skip_vol_regimes or ["Q4"]
        self.min_hold_days = min_hold_days
        self.use_btc_trend_filter = use_btc_trend_filter

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # True Range & ADX
        df["tr"] = np.maximum(
            df["high"] - df["low"],
            np.maximum(
                abs(df["high"] - df["close"].shift(1)),
                abs(df["low"] - df["close"].shift(1))
            )
        )

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

        # Donchian
        for p in self.periods:
            df[f"don_high_{p}"] = df["high"].rolling(p).max().shift(1)
            df[f"don_low_{p}"] = df["low"].rolling(p).min().shift(1)

        # SMA for BTC trend (if needed)
        df["sma_50"] = df["close"].rolling(50).mean()
        df["sma_200"] = df["close"].rolling(200).mean()

        return df

    def get_signal(self, df: pd.DataFrame, btc_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        df = self.calculate_indicators(df)

        if df.empty or len(df) < 30:
            return {"signal": "hold", "reason": "insufficient data"}

        current = df.iloc[-1]
        price = float(current["close"])
        adx = float(current["adx"]) if pd.notna(current["adx"]) else 0
        regime = str(current["vol_regime"]) if pd.notna(current["vol_regime"]) else "Q2"

        # BTC trend filter
        btc_uptrend = True
        if self.use_btc_trend_filter and btc_df is not None and not btc_df.empty:
            btc_ind = self.calculate_indicators(btc_df)
            if len(btc_ind) > 0:
                btc_current = btc_ind.iloc[-1]
                btc_uptrend = (
                    pd.notna(btc_current.get("sma_50")) and
                    pd.notna(btc_current.get("sma_200")) and
                    btc_current["sma_50"] > btc_current["sma_200"]
                )

        # Count signals
        breakout_count = sum(
            1 for p in self.periods
            if pd.notna(current.get(f"don_high_{p}")) and price > current[f"don_high_{p}"]
        )
        breakdown_count = sum(
            1 for p in self.periods
            if pd.notna(current.get(f"don_low_{p}")) and price < current[f"don_low_{p}"]
        )

        adx_pass = adx >= self.adx_threshold
        vol_pass = regime not in self.skip_vol_regimes

        signal = "hold"
        reason = []

        if breakout_count >= self.min_agree:
            if adx_pass and vol_pass and btc_uptrend:
                signal = "buy"
                reason.append(f"breakout {breakout_count}/{len(self.periods)}")
            else:
                if not adx_pass:
                    reason.append(f"ADX {adx:.1f} < {self.adx_threshold}")
                if not vol_pass:
                    reason.append(f"Vol {regime} skipped")
                if not btc_uptrend:
                    reason.append("BTC not in uptrend")
        elif breakdown_count >= self.min_agree:
            signal = "sell"
            reason.append(f"breakdown {breakdown_count}/{len(self.periods)}")

        return {
            "signal": signal,
            "price": price,
            "adx": round(adx, 1),
            "vol_regime": regime,
            "btc_uptrend": btc_uptrend,
            "breakout_count": breakout_count,
            "breakdown_count": breakdown_count,
            "reason": ", ".join(reason) if reason else "no signal",
        }
