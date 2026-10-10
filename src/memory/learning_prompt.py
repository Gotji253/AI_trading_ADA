"""
Helper that prepares a ready-to-use prompt for Hermes to learn from trade memory.
"""

import json
from pathlib import Path

MEMORY_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "trade_memory.json"


def build_learning_prompt() -> str:
    if not MEMORY_FILE.exists():
        return "ยังไม่มีข้อมูลการเทรดเพียงพอ รัน paper trading ให้มีข้อมูลก่อน"

    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        return f"อ่าน memory ไม่ได้: {e}"

    stats = data.get("stats", {})
    lessons = data.get("lessons", [])
    recent = data.get("recent_trades", [])[:5]

    prompt = f"""คุณคือ Hermes Agent ที่ดูแล ADA paper trading

ข้อมูลสถิติล่าสุด:
- จำนวนเทรด: {stats.get('num_trades', 0)}
- Win Rate: {stats.get('win_rate', 0)}%
- Profit Factor: {stats.get('profit_factor', 0)}
- Max Drawdown: {stats.get('max_drawdown_pct', 0)}%
- Total PnL: {stats.get('total_pnl', 0)} USDT

บทเรียนที่ระบบสรุปไว้:
{chr(10).join('- ' + l for l in lessons)}

เทรดล่าสุด 5 รายการ:
{json.dumps(recent, ensure_ascii=False, indent=2)}

จากข้อมูลด้านบน โปรด:
1. เสนอปรับพารามิเตอร์ที่ควรเปลี่ยน (เช่น confidence threshold, MAX_POSITION_PCT, เงื่อนไข multi-tf)
2. ถ้าเห็นรูปแบบที่ทำกำไรซ้ำๆ ให้สร้าง skill ใหม่ที่อธิบายรูปแบบนั้น
3. สรุปเป็นภาษาไทยสั้นๆ ว่าควรทำอะไรต่อ

อย่าเปลี่ยนค่าใดๆถาวร โดยไม่ต้องถามผู้ใช้ก่อน"""
    return prompt.strip()


def main():
    print(build_learning_prompt())


if __name__ == "__main__":
    main()
