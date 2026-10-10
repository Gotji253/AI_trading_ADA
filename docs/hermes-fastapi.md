# Hermes ↔ FastAPI Integration

## 1. รัน FastAPI Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

## 2. ติดตั้ง Skill ใน Hermes

```bash
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-api ~/.hermes/skills/finance/
```

## 3. (แนะนำ) ตั้ง Base URL

```bash
export ADA_API_BASE=http://localhost:8000
```

## 4. ใช้งานใน Hermes

```
/ada-api
ดูสถานะบัญชี

/ada-api
รันรอบเทรดหนึ่งรอบ

/ada-api
สรุปผลงาน

/ada-api
ประวัติการเทรด

/ada-api
สรุปประจำวัน

/ada-api
emergency stop

/ada-api
resume
```

## Endpoints ทั้งหมด

| Method | Path | คำอธิบาย |
|--------|------|----------|
| GET | `/status` | สถานะบัญชี + trading_enabled |
| POST | `/cycle` | รันรอบตัดสินใจ (Alpha → Risk → Execution) |
| GET | `/performance/summary` | สถิติผลงาน |
| GET | `/history?limit=20` | ประวัติการเทรด |
| POST | `/daily-summary` | ส่งสรุปประจำวันไป Telegram |
| POST | `/learn/analyze` | วิเคราะห์ + แนะนำการปรับปรุง |
| POST | `/emergency/stop` | ปิดทุกตำแหน่ง + หยุดเทรด |
| POST | `/emergency/resume` | เปิดการเทรดใหม่ |

## หมายเหตุ

- Hermes เป็น Voice/Chat Interface
- FastAPI เป็นตัวประมวลผลการทำงานจริง
- แยกบทบาทชัดเจน (Alpha / Risk / Execution)
- มี Kill Switch + Resume
