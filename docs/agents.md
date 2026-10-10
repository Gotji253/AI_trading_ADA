# Multi-Agent Architecture

## Agents ทั้งหมด

| Agent | หน้าที่ |
|-------|--------|
| **Alpha_Agent** | หาจังหวะเทรด (Multi-TF + S/R) |
| **Risk_Agent** | คุมขนาดไม้, Daily loss, Drawdown, Position sizing |
| **Execution_Agent** | จำลองเทรด (Paper) / ตรวจ SL-TP |
| **Regime_Agent** | จำแนกสภาวะตลาด (Trending / Ranging / High Volatility) |
| **Attribution_Agent** | วิเคราะห์ผลการเทรดย้อนหลัง สร้าง Matrix |
| **Manager_Agent** | ประสานงานทั้งหมด |

## Regime_Agent

จำแนกสภาวะตลาดเป็น:
- `trending_bull` / `trending_bear` → ให้ใช้ Trend Following
- `ranging` → ให้ใช้ Mean Reversion
- `high_volatility` → ลดขนาดไม้หรือรอ

ระบบใช้ข้อมูลนี้ปรับสัญญาณของ Alpha ใน Manager

## Attribution_Agent

ทำงานร่วมกับ `/learn/analyze`

สร้าง:
- Win Rate แยกตาม Regime
- Attribution matrix (ประเภทการแพ่/ชนะ)
- Insight สั้นๆ

## การทำงานร่วมกัน

```bash
# ดูสภาวะตลาดปัจจุบัน
curl http://localhost:8000/status   # มี current_regime

# วิเคราะห์แบบสมบูรณ์ (รวม Attribution)
curl -X POST http://localhost:8000/learn/analyze
```
