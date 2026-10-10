"""
Multi-Timeframe Analysis for ADA.
Combines 15m + 1h + 4h signals and ranks strength.
"""

from typing import Dict, Any, List
from src.signals.ada_signals import ADASignalGenerator


class MultiTimeframeAnalyzer:
    INTERVALS = ["15m", "1h", "4h"]

    def __init__(self, source: str = "binance"):
        self.gen = ADASignalGenerator(source=source)

    def analyze(self) -> Dict[str, Any]:
        results = {}
        scores = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        strongest = None
        max_conf = -1

        for tf in self.INTERVALS:
            sig = self.gen.generate(interval=tf, lookback=80)
            results[tf] = sig
            if sig.get("status") == "ok":
                conf = sig.get("confidence", 0)
                signal = sig.get("signal", "hold")
                scores[signal] += conf
                if conf > max_conf:
                    max_conf = conf
                    strongest = tf

        # Consensus
        consensus = max(scores, key=scores.get)
        total_score = sum(scores.values()) or 1
        consensus_strength = round(scores[consensus] / total_score, 2)

        # Agreement count
        signals = [r.get("signal") for r in results.values() if r.get("status") == "ok"]
        agreement = signals.count(consensus) if signals else 0

        return {
            "status": "ok",
            "timeframes": results,
            "consensus": consensus,
            "consensus_strength": consensus_strength,
            "strongest_timeframe": strongest,
            "agreement": f"{agreement}/{len(signals)}",
            "scores": {k: round(v, 2) for k, v in scores.items()},
            "recommendation": self._recommend(consensus, agreement, len(signals), consensus_strength),
        }

    def _recommend(self, consensus: str, agreement: int, total: int, strength: float) -> str:
        if total == 0:
            return "hold"
        if agreement >= 2 and strength >= 0.5:
            return consensus
        if agreement == total and strength >= 0.4:
            return consensus
        return "hold"  # reduce false signals


def main():
    analyzer = MultiTimeframeAnalyzer()
    print(analyzer.analyze())


if __name__ == "__main__":
    main()
