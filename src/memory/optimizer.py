"""
Adaptive Optimization — AI suggests parameter changes based on trade memory and attribution.
"""

import json
from typing import Dict, Any

from src.memory.trade_memory import TradeMemory
from src.memory.attribution import PerformanceAttribution
from src.memory.learning_prompt import build_learning_prompt
from src.analysis.ai_analyzer import ADAAIAnalyzer


class AdaptiveOptimizer:
    def __init__(self):
        self.memory = TradeMemory()
        self.attribution = PerformanceAttribution()

    def suggest(self) -> Dict[str, Any]:
        """Generate parameter suggestions."""
        mem = self.memory.load()
        stats = mem.get("stats", {})
        lessons = mem.get("lessons", [])

        # Build enriched prompt
        base_prompt = build_learning_prompt()
        attr = self.attribution.summarize(mem.get("recent_trades", []), [])

        prompt = f"""{base_prompt}

Performance Attribution:
{json.dumps(attr, ensure_ascii=False, indent=2)}

จากข้อมูลด้านบน โปรดเสนอพารามิเตอร์ที่ควรปรับเป็นรูปแบบ JSON เช่น:
{{
  "rsi_oversold": 30,
  "rsi_overbought": 70,
  "sr_proximity_pct": 1.5,
  "min_agreement": 2,
  "confidence_threshold": 0.5,
  "reason": "เหตุผลสั้นๆ"
}}
ให้เฉพาะค่าที่เหมาะสม ไม่ต้องปรับใหญ่"""

        analyzer = ADAAIAnalyzer()
        try:
            raw = analyzer._call_llm(prompt) if hasattr(analyzer, "_call_llm") else prompt
        except Exception as e:
            raw = f"Error: {e}"

        # Try to extract JSON suggestion
        suggestion = self._extract_json(raw)

        return {
            "status": "ok",
            "attribution": attr,
            "raw_suggestion": raw,
            "parsed_suggestion": suggestion,
            "current_stats": stats,
        }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception:
            pass
        return {"error": "Could not parse suggestion"}
