"""
Performance Attribution — classify why trades won or lost.
Taxonomy: False Breakout, High Volatility Slippage, Trend Reversal, Ranging Chop, Good Trend Follow, etc.
"""

from typing import Dict, Any, List


class PerformanceAttribution:
    TAXONOMY = [
        "false_breakout",
        "high_volatility_slippage",
        "trend_reversal",
        "ranging_chop",
        "good_trend_follow",
        "early_exit",
        "late_entry",
        "unknown",
    ]

    def classify(self, trade: Dict[str, Any], entry_snapshot: Dict[str, Any]) -> str:
        """Simple rule-based classification. Can be replaced with LLM later."""
        pnl = trade.get("pnl", 0)
        reason = trade.get("reason", "")
        regime = trade.get("regime", "unknown")

        if pnl > 0:
            if regime in ("bullish", "bearish"):
                return "good_trend_follow"
            return "good_trade"

        # Losses
        if reason == "stop_loss":
            if regime == "sideways":
                return "ranging_chop"
            return "trend_reversal"

        if reason == "signal":
            return "false_breakout"

        if abs(pnl) > 0 and regime == "sideways":
            return "ranging_chop"

        return "unknown"

    def summarize(self, trades: List[Dict], logs: List[Dict]) -> Dict[str, Any]:
        """Aggregate classification counts."""
        counts = {k: 0 for k in self.TAXONOMY}
        classified = []

        # Simple pairing of entry/exit logs by trade_id if available
        for t in trades:
            cls = self.classify(t, {})
            counts[cls] = counts.get(cls, 0) + 1
            classified.append({"trade": t.get("closed_at"), "class": cls, "pnl": t.get("pnl")})

        return {
            "counts": counts,
            "classified_sample": classified[-10:],
            "total": len(trades),
        }
