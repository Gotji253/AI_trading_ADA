"""
3-Dimension Market Analysis for ADA
1. Technical (Multi-TF: 4h Macro, 1h Structure, 15m Trigger)
2. On-Chain (Koios)
3. Sentiment & News
"""

from typing import Dict, Any

from src.signals.multi_tf import MultiTimeframeAnalyzer
from src.analysis.levels import SupportResistance
from src.data.onchain import CardanoOnChain
from src.data.news import NewsSentiment
from src.agents.regime_agent import RegimeAgent


class MarketAnalyzer:
    def __init__(self):
        self.multi = MultiTimeframeAnalyzer()
        self.levels = SupportResistance()
        self.onchain = CardanoOnChain()
        self.news = NewsSentiment()
        self.regime = RegimeAgent()

    def analyze(self) -> Dict[str, Any]:
        """Full 3-dimension analysis."""
        # 1. Technical Multi-TF
        multi = self.multi.analyze()
        levels = self.levels.find_levels(interval="1h")
        regime = self.regime.classify()

        # Extract TF-specific views
        tf_4h = multi.get("timeframes", {}).get("4h", {})
        tf_1h = multi.get("timeframes", {}).get("1h", {})
        tf_15m = multi.get("timeframes", {}).get("15m", {})

        technical = {
            "macro_4h": {
                "signal": tf_4h.get("signal"),
                "price": tf_4h.get("price"),
                "ema20": tf_4h.get("ema20"),
                "ema50": tf_4h.get("ema50"),
                "bias": "bullish" if tf_4h.get("price", 0) > tf_4h.get("ema50", 0) else "bearish",
            },
            "structure_1h": {
                "signal": tf_1h.get("signal"),
                "rsi": tf_1h.get("rsi"),
                "macd_hist": tf_1h.get("macd_hist"),
            },
            "trigger_15m": {
                "signal": tf_15m.get("signal"),
                "rsi": tf_15m.get("rsi"),
            },
            "levels": levels,
            "regime": regime,
            "consensus": multi.get("recommendation"),
            "agreement": multi.get("agreement"),
        }

        # 2. On-Chain
        tip = self.onchain.get_tip()
        epoch = self.onchain.get_epoch_info()
        onchain = {
            "tip": tip,
            "epoch": epoch,
            "health": "stable" if tip.get("status") == "ok" else "unknown",
        }

        # 3. Sentiment
        news = self.news.get_ada_news()
        sentiment = "neutral"
        if news.get("articles"):
            sentiment = self.news.simple_sentiment(news["articles"])

        sentiment_data = {
            "score": sentiment,
            "articles_count": len(news.get("articles", [])),
            "source": news.get("source", "fallback"),
        }

        # Overall bias
        overall = self._overall_bias(technical, onchain, sentiment_data)

        return {
            "status": "ok",
            "technical": technical,
            "onchain": onchain,
            "sentiment": sentiment_data,
            "overall_bias": overall,
            "recommendation": multi.get("recommendation", "hold"),
        }

    def _overall_bias(self, tech: Dict, onchain: Dict, sentiment: Dict) -> str:
        score = 0
        # Technical weight
        if tech.get("macro_4h", {}).get("bias") == "bullish":
            score += 2
        elif tech.get("macro_4h", {}).get("bias") == "bearish":
            score -= 2

        if tech.get("consensus") == "buy":
            score += 1
        elif tech.get("consensus") == "sell":
            score -= 1

        # Sentiment
        if sentiment.get("score") == "positive":
            score += 1
        elif sentiment.get("score") == "negative":
            score -= 1

        # On-chain health (soft)
        if onchain.get("health") == "stable":
            score += 0.5

        if score >= 2:
            return "bullish"
        elif score <= -2:
            return "bearish"
        return "neutral"
