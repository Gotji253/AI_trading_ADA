# Regime_Agent Accuracy Validation

## 1. รันด้วยข้อมูลจริง (API)

```bash
python -m src.backtest.regime_validator
```

## 2. รันด้วยข้อมูลจำลอง

```bash
python -m src.backtest.regime_validator_synthetic
```

## 3. รันด้วยไฟล์ CSV จาก Binance (แนะนำ)

### วิธีใช้

1. ดาวน์โหลดข้อมูล OHLCV จาก Binance (เช่น 1h)
2. บันทึกเป็น CSV ที่มีคอลัมน์อย่างน้อย:
   - `open`, `high`, `low`, `close`, `volume`
   - คอลัมน์เวลา (ถ้ามี): `timestamp`, `open_time`, `date` ฯลฯ

3. รันคำสั่ง:

```bash
python -m src.backtest.regime_validator_csv data/ada_1h.csv
```

### ตัวอย่างเพิ่มเติม

```bash
python -m src.backtest.regime_validator_csv data/ada_1h.csv --forward 24 --step 4
```

### ตัวอย่างรูปแบบ CSV

| คอลัมน์ | จำเป็น |
|---------|--------|
| open | ราคาเปิด |
| high | ราคาสูงสุด |
| low | ราคาต่ำสุด |
| close | ราคาปิด |
| volume | ปริมาณซื้อขาย |
| timestamp / open_time / date | เวลา (ไม่บังคับแต่แนะนำ) |

## ผลลัพธ์

- Overall Accuracy
- Accuracy แยกตาม Regime
- Accuracy เฉพาะตัวอย่างที่ Confidence สูง
