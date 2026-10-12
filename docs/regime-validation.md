# Regime_Agent Accuracy Validation

## รันด้วยข้อมูลจริง

```bash
python -m src.backtest.regime_validator
```

## รันด้วยข้อมูลจำลอง (ไม่ต้อง API)

```bash
python -m src.backtest.regime_validator_synthetic
```

## สิ่งที่ทดสอบ

ระบบตรวจว่า regime ที่บอกตรงกับการเคลื่อนไหวของราคาในช่วงถัดไปหรือไม่

## หมายเหตุ

ข้อมูลจำลองใช้เพื่อทดสอบ logic เท่านั้น ไม่ใช่การรับรองความแม่นยำในตลาดจริง
