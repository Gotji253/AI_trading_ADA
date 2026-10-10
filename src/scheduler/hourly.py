"""
Hourly analysis runner (for cron or Hermes scheduler).
Sends Telegram alert if configured.
"""

import json
from datetime import datetime, timezone

from src.signals.multi_tf import MultiTimeframeAnalyzer
from src.analysis.levels import SupportResistance
from src.data.news import NewsSentiment
from src.data.onchain import CardanoOnChain
from src.memory.trade_memory import TradeMemory
from src.notify.telegram import TelegramNotifier


def run_hourly_analysis(send_telegram: bool = True) -> dict:
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "multi_tf": MultiTimeframeAnalyzer().analyze(),
        "levels": SupportResistance().find_levels(),
        "news": NewsSentiment().get_ada_news(limit=3),
        "onchain": CardanoOnChain().get_tip(),
    }

    try:
        result["memory"] = TradeMemory().update_from_paper()
    except Exception as e:
        result["memory_error"] = str(e)

    consensus = result["multi_tf"].get("consensus", "hold")
    strength = result["multi_tf"].get("consensus_strength", 0)
    strongest = result["multi_tf"].get("strongest_timeframe", "-")
    nearest_sup = result["levels"].get("nearest_support")
    nearest_res = result["levels"].get("nearest_resistance")

    alert_text = (
        f"ADA Hourly Report\n"
        f"Consensus: {consensus.upper()} (strength {strength})\n"
        f"Strongest TF: {strongest}\n"
        f"Support: {nearest_sup} | Resistance: {nearest_res}\n"
        f"Time: {result['timestamp']}"
    )
    result["alert"] = alert_text

    if send_telegram:
        notifier = TelegramNotifier()
        sent = notifier.send(alert_text)
        result["telegram_sent"] = sent

    return result


def main():
    report = run_hourly_analysis()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
