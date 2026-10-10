"""
Alpha_Agent — หาจังหวะเทรด / สร้างสัญญาณ
ใช้ Multi-Timeframe + Support/Resistance + technical signals
"""

from typing import Dict, Any

from src.signals.multi_tf import MultiTimeframeAnalyzer
from src.analysis.levels import SupportResistance


class AlphaAgent:
    def __init__(self):
        self.multi = MultiTimeframeAnalyzer()
        self.levels = SupportResistance()

    def generate_signal(self) -> Dict[str, Any]:
        multi = self.multi.analyze()
        levels = self.levels.find_levels(interval="1h")

        recommendation = multi.get("recommendation", "hold")
        price = levels.get("current_price")

        # Basic confidence from multi-tf strength
        strength = multi.get("consensus_strength", 0)
        confidence = round(min(strength, 1.0), 2)

        return {
            "agent": "alpha",
            "signal": recommendation,
            "confidence": confidence,
            "price": price,
            "multi_tf": multi,
            "levels": levels,
            "reasons": [
                f"Multi-TF consensus: {multi.get('consensus')}",
                f"Agreement: {multi.get('agreement')}",
                f"Strongest TF: {multi.get('strongest_timeframe')}",
            ],
        }
