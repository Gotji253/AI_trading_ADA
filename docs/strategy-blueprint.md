# Systematic Trade Blueprint

## สัญญาณคุณภาพสูง (High Quality Setup) — เกณฑ์ยืดหยุ่น

### Long (Pullback to Support)
1. Regime = `trending_bull` หรือ `mixed`
2. ราคาใกล้แนวรับ ≤ **2.0%**
3. RSI 15m < **45** และ RSI 1h < **60**

### Short (Rally to Resistance)
1. Regime = `trending_bear` หรือ `mixed`
2. ราคาใกล้แนวต้าน ≤ **2.0%**
3. RSI 15m > **55** และ RSI 1h > **40**

## ค่าที่ปรับได้ใน `.env`

```bash
SR_PROXIMITY_PCT=2.0
RSI_LONG_15M=45
RSI_LONG_1H=60
RSI_SHORT_15M=55
RSI_SHORT_1H=40
```

## เปรียบเทียบกับเกณฑ์เดิม

| เกณฑ์ | เดิม | ใหม่ (ยืดหยุ่น) |
|--------|------|-----------------|
| ระยะใกล้แนว | 1.5% | **2.0%** |
| RSI Long 15m | < 40 | **< 45** |
| RSI Long 1h | < 55 | **< 60** |
| RSI Short 15m | > 60 | **> 55** |
| RSI Short 1h | > 45 | **> 40** |
| Regime | เฉพาะ trending | trending + mixed |
