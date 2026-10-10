"""
Memory of paper trade results for AI learning.
Stores summary that can be fed back into analysis prompts.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

from src.paper.trader import PaperTrader


MEMORY_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "trade_memory.json"


class TradeMemory:
    def __init__(self):
        self.path = MEMORY_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def update_from_paper(self) -> Dict[str, Any]:
        """Pull latest stats from paper trader and save memory summary."""
        trader = PaperTrader()
        stats = trader.performance_stats()
        recent = trader.history(limit=10)

        memory = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": stats,
            "recent_trades": recent,
            "lessons": self._extract_lessons(recent, stats),
        }
        self.path.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
        return memory

    def load(self) -> Dict[str, Any]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _extract_lessons(self, trades: List[Dict], stats: Dict) -> List[str]:
        lessons = []
        if not trades:
            return ["No trades yet. Collect more data."]
        if stats.get("win_rate", 0) < 40:
            lessons.append("Win rate is low. Consider tightening entry conditions or using multi-timeframe confirmation.")
        if stats.get("max_drawdown_pct", 0) > 15:
            lessons.append("Drawdown is high. Reduce position size or add stricter stop-loss.")
        if stats.get("profit_factor", 0) < 1:
            lessons.append("Profit factor < 1. Strategy is currently losing money in paper. Review signals.")
        else:
            lessons.append("Profit factor is positive. Continue monitoring.")
        return lessons


def main():
    mem = TradeMemory()
    print(mem.update_from_paper())


if __name__ == "__main__":
    main()
