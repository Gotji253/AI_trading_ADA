# Self-Improvement Engine Architecture

## Continuous Feedback Cycle

```
Data Logging → Performance Attribution → Adaptive Optimization → Walk-Forward Validation → (Approve / Reject)
```

## 1. Data Logging (Micro)

- บันทึก snapshot ตลาดณ จังหวะเข้าเทรด
- RSI, MACD, EMA, แนวรับ/ต้าน, Multi-TF agreement, sentiment
- เหตุผลของ Alpha และข้อจำกัดของ Risk
- ไฟล์: `data/trade_logs.jsonl`

## 2. Performance Attribution

จัดประเภทการแพ่/ชนะ:
- `false_breakout`
- `ranging_chop`
- `trend_reversal`
- `high_volatility_slippage`
- `good_trend_follow`

## 3. Adaptive Optimization

- AI วิเคราะห์ Trade Memory + Attribution
- เสนอปรับ RSI threshold, SR proximity, agreement strictness ฯลฯ
- คืนเป็น JSON suggestion

## 4. Walk-Forward Validation Gate

- พารามิเตอร์ใหม่ต้องผ่าน backtest สั้นๆ ก่อนอนุมัติ
- ถ้าไม่ผ่าน → ไม่อัปเดตไปใช้จริง

## การใช้งาน

```bash
# รันวงจรเต็ม
python -m src.memory.self_improve

# หรือผ่าน API
curl -X POST http://localhost:8000/learn/analyze
```

## ความปลอดภัย

- พารามิเตอร์ใหม่จะไม่ถูกใช้จนกว่าจะผ่าน validation
- ยังเป็น Paper mode เท่านั้น
