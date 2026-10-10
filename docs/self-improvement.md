# Self-Improvement Loop (4-Stage Quarantine Pipeline)

## วงจรที่ปลอดภัย

```
1. Micro Data Logging
        ↓
2. Performance Attribution (Attribution_Agent)
        ↓
3. Adaptive Optimization (/learn/analyze)
        ↓
4. Walk-Forward Validation (Sharpe > 1.5, DD < 8%)
        ↓
   Approve → เสนอผ่าน Hermes / Telegram
   Reject  → ไม่อัปเดต
```

## Stage 1: Micro Data Logging

บันทึกรายละเอียดตอนเข้า/ปิดตำแหน่ง:
- Indicators (RSI, MACD, EMA)
- Volatility (ATR โดยประมาณ)
- Slippage (โดยประมาณ)
- Filter rules ที่ผ่าน
- Regime ณ ขณะเข้า

ไฟล์: `data/trade_logs.jsonl`

## Stage 2: Performance Attribution

**Attribution_Agent** จัดประเภท:
- Win — Trend Following Accuracy
- Loss — False Breakout
- Loss — High Slippage
- Loss — Unexpected News Volatility
- Loss — Ranging Chop

## Stage 3: Adaptive Optimization

- เรียก `POST /learn/analyze`
- AI วิเคราะห์แล้วเสนอปรับพารามิเตอร์
- ตัวอย่าง: เพิ่มระยะ SL ถ้าถูก Whipsaw บ่อย, ปรับ agreement threshold ฯลฯ

## Stage 4: Walk-Forward Validation

เกณฑ์การอนุมัติ:
- Sharpe Ratio > **1.5**
- Max Drawdown < **8%**
- Return เป็นบวก

หากไม่ผ่าน → ไม่อัปเดตค่า

หากผ่าน → ส่งเสนอผ่าน Hermes หรือ Telegram ให้ผู้ใช้ตัดสินใจ

## การใช้งาน

```bash
# รันวงจรเต็ม (4 stages)
python -m src.memory.self_improve

# ผ่าน API
curl -X POST http://localhost:8000/learn/analyze
```

## ความปลอดภัย

- พารามิเตอร์ใหม่จะไม่ถูกใช้จนกว่าจะผ่าน Stage 4
- ยังเป็น Paper mode
- ผล validation ถูกบันทึกไว้ใน response
