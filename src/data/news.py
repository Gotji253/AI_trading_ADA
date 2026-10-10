"""
Free crypto news / sentiment for ADA.
Uses public free endpoints where possible.
"""

from typing import Dict, Any, List
import requests


class NewsSentiment:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AI_trading_ADA/1.0"})

    def get_ada_news(self, limit: int = 5) -> Dict[str, Any]:
        """Try free news source. Fallback to simple message if unavailable."""
        # cryptocurrency.cv free API (no key)
        try:
            url = "https://cryptocurrency.cv/api/news"
            r = self.session.get(url, params={"q": "Cardano OR ADA", "limit": limit}, timeout=15)
            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", data) if isinstance(data, dict) else data
                if isinstance(articles, list):
                    cleaned = []
                    for a in articles[:limit]:
                        cleaned.append({
                            "title": a.get("title") or a.get("headline"),
                            "url": a.get("url") or a.get("link"),
                            "source": a.get("source") or a.get("source_name"),
                            "published": a.get("published") or a.get("posted_at"),
                        })
                    return {"status": "ok", "source": "cryptocurrency.cv", "articles": cleaned}
        except Exception:
            pass

        # Fallback: CoinGecko public status / simple
        return {
            "status": "degraded",
            "message": "Free news API temporarily unavailable. Check manually or add COINGECKO_API_KEY for pro news.",
            "articles": [],
        }

    def simple_sentiment(self, articles: List[Dict]) -> str:
        """Very basic keyword sentiment."""
        if not articles:
            return "neutral"
        text = " ".join(str(a.get("title", "")).lower() for a in articles)
        positive = ["bull", "rally", "surge", "gain", "partnership", "upgrade", "adoption"]
        negative = ["crash", "dump", "hack", "scam", "delay", "lawsuit", "bear"]
        pos = sum(1 for w in positive if w in text)
        neg = sum(1 for w in negative if w in text)
        if pos > neg:
            return "positive"
        if neg > pos:
            return "negative"
        return "neutral"


def main():
    ns = NewsSentiment()
    result = ns.get_ada_news()
    print(result)


if __name__ == "__main__":
    main()
