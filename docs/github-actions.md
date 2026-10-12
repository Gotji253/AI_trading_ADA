# GitHub Actions for Accuracy Testing

## วัตถุประสงค์

ใช้ GitHub Actions runner เพื่อดึงข้อมูลจาก Binance (ไม่ถูกบล็อกเหมือนกับสภาพแวดล้อม)

## วิธีใช้งาน

### 1. รันมือผ่าน GitHub

1. ไปที่แท็บ **Actions** ใน repository
2. เลือก workflow **Accuracy Test (Binance)**
3. กด **Run workflow**

### 2. รันอัตโนมัติ

Workflow จะรันทุกวันจันทร์เวลา 02:00 UTC

## สิ่งที่ทดสอบ

- Regime_Agent accuracy (Binance data)
- Synthetic regime test
- ผลลัพธ์จะถูกบันทึกใน Artifacts

## หมายเหตุ

- GitHub Actions runner สามารถเข้า Binance API ได้
- ไม่ต้องใส่ API Key สำหรับการดึงข้อมูลสาธารณะ
- ผลลัพธ์จะปรากฏในแท็บ Actions
