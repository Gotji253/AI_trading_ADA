"""
Hourly analysis runner (for cron or Hermes scheduler).
Sends natural Thai Telegram alert if configured.
"""

import json
from datetime import datetime, timezone

from src.signals.multi_tf import MultiTimeframeAnalyzer
from src.analysis.levels import SupportResistance
from src.data.news import NewsSentiment
from src.data.onchain import CardanoOnChain
from src.memory.trade_memory import TradeMemory
from src.notify.telegram import TelegramNotifier


def _consensus_thai(consensus: str) -> str:
    mapping = {
        "buy": "น่าซื้อ",
        "sell": "น่าขาย",
        "hold": "ถือรอ",
    }
    return mapping.get(consensus.lower(), consensus)


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
    price = result["levels"].get("current_price")

    thai_consensus = _consensus_thai(consensus)
    strength_text = "แข็ง" if strength >= 0.6 else "ปานกลาง" if strength >= 0.4 else "อ่อน"

    alert_text = (
        f"สรุป ADA รายชั่วโมง\n\n"
        f"สัญญาณหลัก: {thai_consensus} ({strength_text})\n"
        f"ราคาปัจจุบัน: {price} USDT\n"
        f"ไทม์เฟรมที่แข็งที่สุด: {strongest}\n"
        f"แนวรับรับ: {nearest_sup or '-'}\n"
        f"แนวต้าน: {nearest_res or '-'}\n\n"
        f"นี้เป็นการวิเคราะห์เท่านั้น ยังไม่ได้เทรดจริง"
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
