"""
Alpha_Agent — หาจังหวะเทรด
ใช้กรอบวิเคราะห์ 3 มิติ: Technical Multi-TF + On-Chain + Sentiment
"""

from typing import Dict, Any

from src.analysis.market_analyzer import MarketAnalyzer


class AlphaAgent:
    def __init__(self):
        self.analyzer = MarketAnalyzer()

    def generate_signal(self) -> Dict[str, Any]:
        analysis = self.analyzer.analyze()

        technical = analysis.get("technical", {})
        recommendation = analysis.get("recommendation", "hold")
        overall_bias = analysis.get("overall_bias", "neutral")
        price = technical.get("levels", {}).get("current_price")

        # Confidence based on agreement + bias alignment
        agreement_str = technical.get("agreement", "0/0")
        try:
            agree_num = int(agreement_str.split("/")[0])
        except Exception:
            agree_num = 0

        confidence = 0.3
        if agree_num >= 2 and overall_bias in ("bullish", "bearish"):
            confidence = 0.7
        elif agree_num >= 2:
            confidence = 0.5

        reasons = [
            f"Multi-TF recommendation: {recommendation}",
            f"Overall bias: {overall_bias}",
            f"4h bias: {technical.get('macro_4h', {}).get('bias')}",
            f"Regime: {technical.get('regime', {}).get('regime')}",
            f"Sentiment: {analysis.get('sentiment', {}).get('score')}",
            f"On-chain health: {analysis.get('onchain', {}).get('health')}",
        ]

        return {
            "agent": "alpha",
            "signal": recommendation,
            "confidence": round(confidence, 2),
            "price": price,
            "overall_bias": overall_bias,
            "analysis": analysis,
            "reasons": reasons,
        }
