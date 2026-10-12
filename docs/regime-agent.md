# Regime_Agent (Improved)

## สิ่งที่ปรับปรุง

- ใช้ **1h + 4h** ร่วมกัน
- เพิ่ม **EMA structure** บน 4h (EMA20 vs EMA50)
- Threshold ปรับได้ผ่าน `.env`
- มี **Hysteresis** เพื่อลดการสลับสภาวะบ่อยเกินไป

## Regime ที่จำแนกได้

| Regime | เหตุผล | Strategy Hint |
|--------|----------|---------------|
| `trending_bull` | ตลาดขึ้นแรง + EMA bias bullish | trend_following |
| `trending_bear` | ตลาดลงแรง + EMA bias bearish | trend_following |
| `ranging` | Trend ต่ำ | mean_reversion |
| `high_volatility` | Vol หรือ Range สูง | reduce_size_or_wait |
| `mixed` | สภาวะปน | neutral |

## ค่าที่ปรับได้ (`.env`)

```bash
REGIME_TREND_THRESHOLD=3.5
REGIME_VOL_HIGH=4.5
REGIME_RANGE_HIGH=2.8
REGIME_RANGING_THRESHOLD=1.8
```

## การใช้งาน

Regime จะถูกเรียกทุกครั้งที่ Manager รัน `/cycle`  
และถูกใช้ปรับสัญญาณของ Alpha (โดยเฉพาะใน high volatility)
