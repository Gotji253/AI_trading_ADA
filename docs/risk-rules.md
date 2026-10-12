# Risk Management Rules (Improved)

## กฎหลัก

| กฎ | ค่าเริ่มต้น | คำอธิบาย |
|-----|-----------|----------|
| Risk per Trade | 1.5% | ความเสี่ยงสูงสุดต่อไม้ |
| Daily Loss Limit | 4% | หยุดเทรดใหม่ในวันนั้น |
| Max Drawdown Hard Stop | 12% | เข้า Quarantine Mode |
| **Max Open Risk** | 3% | จำกัดความเสี่ยงรวม |
| **Consecutive Loss Limit** | 3 ครั้ง | หยุดชั่วคราว |
| **Cooldown** | 30 นาที | หลังขาดทุนติด |

## สิ่งที่ปรับปรุงใหม่

### 1. Max Open Risk
จำกัดความเสี่ยงรวมของทุกตำแหน่งไม่ให้เกินค่าที่กำหนด

### 2. Volatility Adjustment
- ATR > 2.5% → ลดขนาดไม้เหลือ 50%
- ATR > 1.5% → ลดขนาดไม้เหลือ 25%
- Regime = high_volatility → ลดขนาดไม้เพิ่ม

### 3. Consecutive Loss Cooldown
หลังขาดทุนติด 3 ครั้ง → หยุดเทรดใหม่ 30 นาที

## ค่าที่ปรับได้ใน `.env`

```bash
RISK_PER_TRADE_PCT=1.5
DAILY_LOSS_LIMIT_PCT=4
MAX_DRAWDOWN_HARD_STOP_PCT=12
MAX_OPEN_RISK_PCT=3.0
CONSECUTIVE_LOSS_LIMIT=3
LOSS_COOLDOWN_MINUTES=30
```
