# Strict Risk Management Rules

## 1. Risk Per Trade
- ขนาดไม้ต่อตำแหน่งไม่เกิน **1% - 2%** ของ Equity ณ ขณะนั้น
- ตั้งค่าด้วย `RISK_PER_TRADE_PCT` (ค่าเริ่มต้น 1.5)

## 2. Daily Loss Limit
- หากขาดทุนรวมในวันแตะ **3% - 5%** ของ Capital
- ระบบสั่ง **Pause** การเทรดใหม่ทันทีจนกว่าวันถัดไป
- ตั้งค่าด้วย `DAILY_LOSS_LIMIT_PCT` (ค่าเริ่มต้น 4)

## 3. Max Drawdown Hard Stop
- หาก Drawdown สะสมแตะ **10% - 15%**
- ระบบยิง `/emergency/stop` อัตโนมัติ
- เข้า **Quarantine Mode** (หยุดเทรดทั้งหมด)
- ต้องทำ Debug / Backtest ใหม่ก่อนเปิดการเทรดใหม่
- ตั้งค่าด้วย `MAX_DRAWDOWN_HARD_STOP_PCT` (ค่าเริ่มต้น 12)

## การทำงาน

1. ทุกรอบ `/cycle` ระบบตรวจกฎทั้งหมด
2. ถ้าถึง Max Drawdown → เข้า Quarantine อัตโนมัติ
3. ถ้าถึง Daily Loss Limit → ปฏิเสธเทรดใหม่ในวันนั้น
4. ขนาดไม้คำนวนจากระยะถึง SL ไม่เกินค่าที่กำหนด

## คำสั่งที่เกี่ยวข้อง

ดูใน `.env.example` และเอกสารไปใส่ `.env`
