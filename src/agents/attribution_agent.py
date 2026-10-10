"""
Attribution_Agent — Self-Reflection Analyst
วิเคราะห์ประวัติการเทรด สร้าง Matrix เช่น Win Rate ตาม Volatility, Risk-Reward accuracy ฯลฯ
"""

from typing import Dict, Any, List
from collections import defaultdict

from src.memory.trade_memory import TradeMemory
from src.memory.attribution import PerformanceAttribution


class AttributionAgent:
    def __init__(self):
        self.memory = TradeMemory()
        self.attr = PerformanceAttribution()

    def analyze(self) -> Dict[str, Any]:
        """สร้างรายงานวิเคราะห์เองจากประวัติการเทรด"""
        mem = self.memory.load()
        trades = mem.get("recent_trades", [])

        if not trades:
            return {"status": "ok", "message": "No trades to analyze", "matrices": {}}

        # Win rate by regime (if available)
        by_regime = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0.0})
        by_class = defaultdict(lambda: {"count": 0, "pnl": 0.0})

        for t in trades:
            regime = t.get("regime", "unknown")
            pnl = t.get("pnl", 0)
            cls = self.attr.classify(t, {})

            by_regime[regime]["total"] += 1
            by_regime[regime]["pnl"] += pnl
            if pnl > 0:
                by_regime[regime]["wins"] += 1

            by_class[cls]["count"] += 1
            by_class[cls]["pnl"] += pnl

        # Build matrices
        regime_matrix = {}
        for r, data in by_regime.items():
            wr = round(data["wins"] / data["total"] * 100, 1) if data["total"] else 0
            regime_matrix[r] = {
                "trades": data["total"],
                "win_rate": wr,
                "total_pnl": round(data["pnl"], 2),
                "avg_pnl": round(data["pnl"] / data["total"], 2) if data["total"] else 0,
            }

        class_matrix = {
            k: {"count": v["count"], "total_pnl": round(v["pnl"], 2)}
            for k, v in by_class.items()
        }

        # Overall
        total_trades = len(trades)
        total_wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
        overall_wr = round(total_wins / total_trades * 100, 1) if total_trades else 0

        return {
            "status": "ok",
            "total_trades": total_trades,
            "overall_win_rate": overall_wr,
            "regime_matrix": regime_matrix,
            "attribution_matrix": class_matrix,
            "insight": self._insight(regime_matrix, class_matrix),
        }

    def _insight(self, regime_m: Dict, class_m: Dict) -> str:
        if not regime_m:
            return "ยังไม่มีข้อมูลเพียงพอสำหรับวิเคราะห์"

        best = max(regime_m.items(), key=lambda x: x[1].get("win_rate", 0), default=None)
        worst = min(regime_m.items(), key=lambda x: x[1].get("win_rate", 0), default=None)

        parts = []
        if best and best[1]["trades"] >= 2:
            parts.append(f"ทำได้ดีที่สุดในสภาวะ {best[0]} (Win Rate {best[1]['win_rate']}%)")
        if worst and worst[1]["trades"] >= 2 and worst[0] != (best[0] if best else None):
            parts.append(f"ควรระวังในสภาวะ {worst[0]}")

        return "; ".join(parts) if parts else "ข้อมูลยังไม่เพียงพอสำหรับสรุปแนวโน้ม"
