"""
Regime_Agent Accuracy Validator
ทดสอบว่า regime ที่ระบบบอกตรงกับการเคลื่อนไหวของราคาในช่วงถัดไปหรือไม่
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

from src.agents.regime_agent import RegimeAgent
from src.data.ada_price import ADAPriceFetcher


class RegimeValidator:
    def __init__(self, source: str = "binance"):
        self.agent = RegimeAgent(source=source)
        self.fetcher = ADAPriceFetcher(preferred_source=source)

    def validate(
        self,
        lookback_bars: int = 200,
        forward_bars: int = 12,
        step: int = 6,
    ) -> Dict[str, Any]:
        """
        วิ่งตามข้อมูลย้อนหลัง แล้วดูว่าราคาเคลื่อนไหวตาม regime หรือไม่
        """
        df = self.fetcher.get_ohlcv("1h", lookback_bars)
        if df.empty or len(df) < 80:
            return {"status": "error", "message": "Not enough data"}

        results = []
        regimes_seen = []

        # Walk through history
        for i in range(60, len(df) - forward_bars, step):
            # Temporary slice for classification
            slice_df = df.iloc[: i + 1].copy()

            # Monkey-patch fetcher temporarily (simple approach)
            original = self.agent.fetcher.get_with_indicators

            def mock_get(interval="1h", limit=150):
                if interval == "1h":
                    return slice_df.tail(limit)
                # For 4h approximate by resampling
                try:
                    res = slice_df.resample("4h").agg({
                        "open": "first", "high": "max", "low": "min",
                        "close": "last", "volume": "sum"
                    }).dropna()
                    return res.tail(40)
                except Exception:
                    return pd.DataFrame()

            self.agent.fetcher.get_with_indicators = mock_get

            try:
                regime_result = self.agent.classify()
            finally:
                self.agent.fetcher.get_with_indicators = original

            if regime_result.get("status") != "ok":
                continue

            regime = regime_result["regime"]
            confidence = regime_result.get("confidence", 0)

            # Future price movement
            future = df.iloc[i + 1 : i + 1 + forward_bars]
            if future.empty:
                continue

            start_price = float(df["close"].iloc[i])
            end_price = float(future["close"].iloc[-1])
            max_price = float(future["high"].max())
            min_price = float(future["low"].min())

            ret_pct = (end_price / start_price - 1) * 100
            max_up = (max_price / start_price - 1) * 100
            max_down = (min_price / start_price - 1) * 100

            # Score correctness
            correct = self._is_correct(regime, ret_pct, max_up, max_down)

            results.append({
                "index": i,
                "regime": regime,
                "confidence": confidence,
                "return_pct": round(ret_pct, 2),
                "max_up": round(max_up, 2),
                "max_down": round(max_down, 2),
                "correct": correct,
            })
            regimes_seen.append(regime)

        if not results:
            return {"status": "error", "message": "No valid samples"}

        return self._summarize(results)

    def _is_correct(self, regime: str, ret: float, max_up: float, max_down: float) -> bool:
        """กฎง่ายๆ ในการตัดสินว่า regime ถูกต้องหรือไม่"""
        if regime == "trending_bull":
            return ret > 0.5 or max_up > 1.5
        if regime == "trending_bear":
            return ret < -0.5 or max_down < -1.5
        if regime == "ranging":
            return abs(ret) < 1.5 and abs(max_up) < 2.5 and abs(max_down) < 2.5
        if regime == "high_volatility":
            return abs(max_up) > 2.0 or abs(max_down) > 2.0
        return False  # mixed / unknown not scored

    def _summarize(self, results: List[Dict]) -> Dict[str, Any]:
        df = pd.DataFrame(results)
        total = len(df)
        correct = df["correct"].sum()
        accuracy = round(correct / total * 100, 1) if total else 0

        by_regime = {}
        for r in df["regime"].unique():
            sub = df[df["regime"] == r]
            by_regime[r] = {
                "count": len(sub),
                "accuracy": round(sub["correct"].mean() * 100, 1),
                "avg_return": round(sub["return_pct"].mean(), 2),
                "avg_confidence": round(sub["confidence"].mean(), 2),
            }

        # High confidence subset
        high_conf = df[df["confidence"] >= 0.65]
        high_acc = round(high_conf["correct"].mean() * 100, 1) if len(high_conf) else 0

        return {
            "status": "ok",
            "total_samples": total,
            "overall_accuracy": accuracy,
            "high_confidence_accuracy": high_acc,
            "high_confidence_samples": len(high_conf),
            "by_regime": by_regime,
            "sample_results": results[-10:],
        }


def main():
    v = RegimeValidator()
    print("Running Regime accuracy validation...")
    result = v.validate(lookback_bars=300, forward_bars=12, step=8)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
