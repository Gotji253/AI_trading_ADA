# Regime_Agent Accuracy Validation

## วิธีรัน

```bash
python -m src.backtest.regime_validator
```

## สิ่งที่ทดสอบ

ระบบวิ่งตามข้อมูลย้อนหลัง แล้วตรวจว่า:

| Regime | ถือว่า“ถูกต้อง”เมื่อ |
|--------|---------------------|
| `trending_bull` | ราคาขึ้นต่อหรือมี upside |
| `trending_bear` | ราคาลงต่อหรือมี downside |
| `ranging` | ราคาไม่เคลื่อนไหวมาก |
| `high_volatility` | มีการเคลื่อนไหวของราคามาก |

## ผลลัพธ์

- Overall Accuracy
- Accuracy แยกตาม Regime
- Accuracy เฉพาะตัวอย่างที่ confidence สูง
- ตัวอย่างผลลัพธ์ล่าสุด

## หมายเหตุ

นี่เป็นการทดสอบแบบง่าย ใช้เพื่อดูแนวโน้มไม่ใช่เป็นการรับรองความแม่นยำแบบสมบูรณ์
