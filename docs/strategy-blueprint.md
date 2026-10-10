# Systematic Trade Blueprint

## สัญญาณที่ชอบ (High Quality Setup)

1. **Regime_Agent** = `trending_bull` (4h bias bullish)
2. ราคาพักตัวลงมาใกล้ **1h Support Zone**
3. บน 15m: RSI < 40 (oversold micro) + rejection บริเวณรับ
4. Multi-TF alignment สูง

## เหตุผล

- 4h Bullish Trend + 1h Pullback to Support + 15m Oversold Trigger
- ความน่าจะเป็นสูง (High Win-Rate Probability)
- ลดโอกาส Chop ใน Sideway เพราะ Regime กรองไว้

## Risk Management (ตาม Blueprint)

| กฎ | ค่า |
|-----|-----|
| Risk per Trade | **1.0%** of Equity |
| Daily Loss Limit | **3.0%** |
| Max Drawdown Hard Stop | **10.0%** → Quarantine |

## จุดแข็งของระบบ

- Regime_Agent + Risk_Agent กรองก่อน Execution
- ลดการถูกตัด SL ในช่วง Sideway
- ลดขนาดไม้ใน High Volatility

## ข้อจำกัดที่ยังเหลือ

- การตรวจจับ Pinbar ยังเป็นแบบประมาณ (rule-based)
- Slippage ยังไม่ได้จำลองใน paper เต็มรูปแบบ
- ต้องพึ่งบาคเทสต์ในสภาวะตลาดต่างๆ
