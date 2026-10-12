# Regime_Agent (Enhanced)

## ความสามารถที่เพิ่มขึ้น

- **ATR (14)** สำหรับวัด volatility
- **EMA200** บน 4h สำหรับ macro bias
- **Volume ratio** (ยืนยันความแข็ง)
- **Confidence score** (0–1)
- Multi-TF (1h + 4h) + Hysteresis

## ผลลัพธ์เพิ่มเติม

```json
{
  "regime": "trending_bull",
  "confidence": 0.78,
  "strategy_hint": "trend_following",
  "atr_pct": 1.42,
  "volume_ratio": 1.15,
  "ema_bias_4h": "strong_bull",
  "ema200_aligned": true
}
```

## การใช้งาน

Regime ถูกใช้ใน Manager ทุกครั้งที่รัน `/cycle`  
Confidence สูง = สัญญาณน่าเชื่อถือมากขึ้น
