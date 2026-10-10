"""
Hourly analysis runner (for cron or Hermes scheduler).
Generates multi-tf + levels + news + on-chain summary and optionally updates memory.
"""

import json
from datetime import datetime, timezone

from src.signals.multi_tf import MultiTimeframeAnalyzer
from src.analysis.levels import SupportResistance
from src.data.news import NewsSentiment
from src.data.onchain import CardanoOnChain
from src.memory.trade_memory import TradeMemory


def run_hourly_analysis() -> dict:
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "multi_tf": MultiTimeframeAnalyzer().analyze(),
        "levels": SupportResistance().find_levels(),
        "news": NewsSentiment().get_ada_news(limit=3),
        "onchain": CardanoOnChain().get_tip(),
    }

    # Update trade memory
    try:
        result["memory"] = TradeMemory().update_from_paper()
    except Exception as e:
        result["memory_error"] = str(e)

    # Simple alert message
    consensus = result["multi_tf"].get("consensus", "hold")
    strength = result["multi_tf"].get("consensus_strength", 0)
    result["alert"] = f"ADA hourly: consensus={consensus} (strength {strength}). Check full report."

    return result


def main():
    report = run_hourly_analysis()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
