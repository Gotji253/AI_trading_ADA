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

## 3. ใช้งานใน Hermes

```
/ada-api
ดูสถานะบัญชี

/ada-api
รันรอบเทรดหนึ่งรอบ

/ada-api
สรุปผลงาน

/ada-api
emergency stop
```

## Endpoints สำคัญ

| Endpoint | คำอธิบาย |
|----------|----------|
| `GET /status` | สถานะบัญชี |
| `POST /cycle` | รันรอบตัดสินใจ |
| `GET /performance/summary` | สถิติผลงาน |
| `POST /learn/analyze` | วิเคราะห์ + แนะนำการปรับปรุง |
| `POST /emergency/stop` | ปิดทุกตำแหน่ง + หยุดเทรด |

## หมายเหตุ

- Hermes เป็น Voice/Chat Interface
- FastAPI เป็นตัวประมวลผลการทำงานจริง
- แยกบทบาทชัดเจน (Alpha / Risk / Execution)
