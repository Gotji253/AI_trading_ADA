"""
3-Dimension Market Analysis for ADA
Enhanced with pullback-to-support + rejection logic for bullish regime.
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
        multi = self.multi.analyze()
        levels = self.levels.find_levels(interval="1h")
        regime = self.regime.classify()

        tf_4h = multi.get("timeframes", {}).get("4h", {})
        tf_1h = multi.get("timeframes", {}).get("1h", {})
        tf_15m = multi.get("timeframes", {}).get("15m", {})

        price = levels.get("current_price") or tf_1h.get("price")
        nearest_sup = levels.get("nearest_support")

        # Enhanced signal logic for bullish pullback setup
        recommendation = "hold"
        setup_quality = "none"

        is_bullish_regime = regime.get("regime") in ("trending_bull",)
        near_support = False
        if price and nearest_sup:
            near_support = abs(price - nearest_sup) / nearest_sup * 100 <= 1.5

        rsi_15m = tf_15m.get("rsi", 50)
        rsi_1h = tf_1h.get("rsi", 50)

        if is_bullish_regime and near_support and rsi_15m < 40 and rsi_1h < 55:
            recommendation = "buy"
            setup_quality = "high"  # Pullback + rejection zone + oversold micro
        elif multi.get("recommendation") in ("buy", "sell"):
            recommendation = multi.get("recommendation")
            setup_quality = "medium"

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
                "rsi": rsi_1h,
                "macd_hist": tf_1h.get("macd_hist"),
                "near_support": near_support,
            },
            "trigger_15m": {
                "signal": tf_15m.get("signal"),
                "rsi": rsi_15m,
            },
            "levels": levels,
            "regime": regime,
            "setup_quality": setup_quality,
            "consensus": multi.get("recommendation"),
            "agreement": multi.get("agreement"),
        }

        tip = self.onchain.get_tip()
        onchain = {
            "tip": tip,
            "health": "stable" if tip.get("status") == "ok" else "unknown",
        }

        news = self.news.get_ada_news()
        sentiment = "neutral"
        if news.get("articles"):
            sentiment = self.news.simple_sentiment(news["articles"])

        sentiment_data = {
            "score": sentiment,
            "articles_count": len(news.get("articles", [])),
        }

        overall = self._overall_bias(technical, onchain, sentiment_data)

        return {
            "status": "ok",
            "technical": technical,
            "onchain": onchain,
            "sentiment": sentiment_data,
            "overall_bias": overall,
            "recommendation": recommendation,
            "setup_quality": setup_quality,
        }

    def _overall_bias(self, tech: Dict, onchain: Dict, sentiment: Dict) -> str:
        score = 0
        if tech.get("macro_4h", {}).get("bias") == "bullish":
            score += 2
        elif tech.get("macro_4h", {}).get("bias") == "bearish":
            score -= 2

        if tech.get("setup_quality") == "high":
            score += 1.5

        if sentiment.get("score") == "positive":
            score += 1
        elif sentiment.get("score") == "negative":
            score -= 1

        if onchain.get("health") == "stable":
            score += 0.5

        if score >= 2.5:
            return "bullish"
        elif score <= -2:
            return "bearish"
        return "neutral"
