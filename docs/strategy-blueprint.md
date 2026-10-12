# Systematic Trade Blueprint

## สัญญาณคุณภาพสูง (High Quality Setup)

### Long (Pullback to Support)
1. **Regime_Agent** = `trending_bull`
2. ราคาพักตัวลงมาใกล้ **1h Support Zone** (≤ 1.5%)
3. บน 15m: RSI < 40 + บน 1h: RSI < 55

### Short (Rally to Resistance)
1. **Regime_Agent** = `trending_bear`
2. ราคาราลลี่ขึ้นมาใกล้ **1h Resistance Zone** (≤ 1.5%)
3. บน 15m: RSI > 60 + บน 1h: RSI > 45

## เหตุผล

- Long: 4h Bullish + 1h Pullback to Support + 15m Oversold
- Short: 4h Bearish + 1h Rally to Resistance + 15m Overbought
- ลดโอกาส Chop ใน Sideway เพราะ Regime กรองไว้

## Risk Management

| กฎ | ค่า |
|-----|-----|
| Risk per Trade | 1.5% |
| Daily Loss Limit | 4% |
| Max Drawdown Hard Stop | 12% |
| Cooldown | ขาดทุนติด 4 ครั้ง → พัก 20 นาที |

## ค่าที่ปรับได้

```bash
SR_PROXIMITY_PCT=1.5
```
