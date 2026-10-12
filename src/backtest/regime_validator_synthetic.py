"""
Regime_Agent Accuracy Validator (Synthetic Data)
ใช้ข้อมูลจำลองเพื่อทดสอบ logic โดยไม่ต้องพึ่ง API ภายนอก
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

from src.agents.regime_agent import RegimeAgent


class SyntheticRegimeValidator:
    def __init__(self):
        self.agent = RegimeAgent(source="binance")

    def _generate_synthetic(self, bars: int = 300, seed: int = 42) -> pd.DataFrame:
        """สร้างข้อมูลราคาจำลองที่มีทั้ง trend, ranging, และ high volatility"""
        np.random.seed(seed)
        dates = pd.date_range("2025-01-01", periods=bars, freq="1h", tz="UTC")

        # Base price
        price = 0.45
        prices = []

        for i in range(bars):
            # Create different regimes over time
            if i < 80:          # ranging
                change = np.random.normal(0, 0.003)
            elif i < 160:       # trending bull
                change = np.random.normal(0.0012, 0.004)
            elif i < 220:       # high volatility
                change = np.random.normal(0, 0.012)
            else:               # trending bear
                change = np.random.normal(-0.001, 0.004)

            price *= (1 + change)
            prices.append(price)

        df = pd.DataFrame({
            "open": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.002))) for p in prices],
            "low":  [p * (1 - abs(np.random.normal(0, 0.002))) for p in prices],
            "close": prices,
            "volume": np.random.uniform(1e6, 5e6, bars),
        }, index=dates)

        # Fix high/low consistency
        df["high"] = df[["open", "high", "close"]].max(axis=1)
        df["low"] = df[["open", "low", "close"]].min(axis=1)

        return df

    def validate(self, bars: int = 280, forward_bars: int = 10, step: int = 8) -> Dict[str, Any]:
        df = self._generate_synthetic(bars)

        results = []

        for i in range(60, len(df) - forward_bars, step):
            slice_df = df.iloc[: i + 1].copy()

            # Mock the fetcher
            original = self.agent.fetcher.get_with_indicators

            def mock_get(interval="1h", limit=150):
                if interval == "1h":
                    return slice_df.tail(min(limit, len(slice_df)))
                # Approximate 4h
                res = slice_df.resample("4h").agg({
                    "open": "first", "high": "max", "low": "min",
                    "close": "last", "volume": "sum"
                }).dropna()
                return res.tail(40)

            self.agent.fetcher.get_with_indicators = mock_get

            try:
                regime_result = self.agent.classify()
            finally:
                self.agent.fetcher.get_with_indicators = original

            if regime_result.get("status") != "ok":
                continue

            regime = regime_result["regime"]
            confidence = regime_result.get("confidence", 0)

            future = df.iloc[i + 1 : i + 1 + forward_bars]
            start_price = float(df["close"].iloc[i])
            end_price = float(future["close"].iloc[-1])
            max_up = (future["high"].max() / start_price - 1) * 100
            max_down = (future["low"].min() / start_price - 1) * 100
            ret_pct = (end_price / start_price - 1) * 100

            correct = self._is_correct(regime, ret_pct, max_up, max_down)

            results.append({
                "regime": regime,
                "confidence": round(confidence, 2),
                "return_pct": round(ret_pct, 2),
                "correct": correct,
            })

        return self._summarize(results)

    def _is_correct(self, regime: str, ret: float, max_up: float, max_down: float) -> bool:
        if regime == "trending_bull":
            return ret > 0.3 or max_up > 1.0
        if regime == "trending_bear":
            return ret < -0.3 or max_down < -1.0
        if regime == "ranging":
            return abs(ret) < 1.2
        if regime == "high_volatility":
            return abs(max_up) > 1.5 or abs(max_down) > 1.5
        return False

    def _summarize(self, results: List[Dict]) -> Dict[str, Any]:
        if not results:
            return {"status": "error", "message": "No samples"}

        df = pd.DataFrame(results)
        total = len(df)
        accuracy = round(df["correct"].mean() * 100, 1)

        by_regime = {}
        for r in df["regime"].unique():
            sub = df[df["regime"] == r]
            by_regime[r] = {
                "count": int(len(sub)),
                "accuracy": round(sub["correct"].mean() * 100, 1),
                "avg_confidence": round(sub["confidence"].mean(), 2),
            }

        high_conf = df[df["confidence"] >= 0.6]
        high_acc = round(high_conf["correct"].mean() * 100, 1) if len(high_conf) else 0

        return {
            "status": "ok",
            "data_type": "synthetic",
            "total_samples": total,
            "overall_accuracy": accuracy,
            "high_confidence_accuracy": high_acc,
            "by_regime": by_regime,
            "note": "ผลจากข้อมูลจำลอง ใช้เพื่อทดสอบ logic เท่านั้น",
        }


def main():
    v = SyntheticRegimeValidator()
    print("Running synthetic Regime accuracy test...")
    result = v.validate()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
