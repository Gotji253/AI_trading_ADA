# Backtest & Walk-Forward Validation

## วัตถุประสงค์

ทดสอบกลยุทธ์ **Multi-Timeframe (15m + 1h + 4h)** ของ Alpha_Agent บนข้อมูลย้อนหลังของ ADA

- จำแนกสภาวะตลาด (Bullish / Bearish / Sideways)
- วัดผลรวมและแยกตาม regime
- Walk-Forward เพื่อตรวจความเสถียรนองกลยุทธ์ในหน้าต่างๆ

## การใช้งาน

```bash
# Backtest ง่าย
python -m src.backtest.cli --mode simple --limit 500

# Walk-Forward
python -m src.backtest.cli --mode walkforward --limit 800
```

## ผลลัพธ์ที่ได้

- จำนวนเทรด, Win Rate, Total PnL, Return %
- ผลแยกตาม regime (bullish / bearish / sideways)
- Equity curve sample
- ผลแต่ละหน้าต่างใน Walk-Forward

## หมายเหตุ

- ใช้ข้อมูลจริงจาก Binance public API
- ตรราสามารถเปลี่ยนกลยุทธ์สัญญาณให้ใกล้เคียงกับ live Alpha_Agent
- อยู่ในโหมด Paper Trading เท่านั้น
- ใช้การจำแนกสภาวะตลาดแบบง่าย (trend + volatility)

## ข้อมูลที่ใช้

- `src/data/ada_price.py` — ดึง OHLCV
- `src/signals/multi_tf.py` — โครงสร้างสัญญาณ
- `src/backtest/engine.py` — เครื่องจำลอง
