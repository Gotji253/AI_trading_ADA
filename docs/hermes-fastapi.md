# Hermes ↔ FastAPI Integration

## ติดตั้งแบบพร้อมใช้งาน (ใส่ API Key แล้วรันได้เลย)

### วิธีที่ 1: ใช้สคริปต์ (แนะนำ)

```bash
bash scripts/setup_hermes.sh
```

### วิธีที่ 2: ทำมือเอง

```bash
# 1. คัดลอก skill
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-api ~/.hermes/skills/finance/

# 2. ตั้งค่า API key
cp .env.example .env
# แก้ไขใน .env:
#   OPENROUTER_API_KEY=sk-or-v1-...
#   TELEGRAM_BOT_TOKEN=...
#   TELEGRAM_CHAT_ID=...

# 3. รัน server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## การใช้งานใน Hermes

```
/ada-api
ดูสถานะ

/ada-api
รันรอบเทรด

/ada-api
สรุปผลงาน

/ada-api
emergency stop
```

## API Keys ที่ต้องใช้

| Key | จำเป็น | จำเป็นไม่ |
|-----|--------|-----------|
| `OPENROUTER_API_KEY` | AI Analysis, Learning | ส่วน AI ใช้ไม่ได้ |
| `TELEGRAM_BOT_TOKEN` | แจ้งเตือน | ส่วนแจ้งเตือนใช้ไม่ได้ |
| `TELEGRAM_CHAT_ID` | แจ้งเตือน | ส่วนแจ้งเตือนใช้ไม่ได้ |
| `BINANCE_API_KEY` | ดึงราคา (optional) | ใช้ public endpoint ได้ |

## Endpoints

| Method | Path | คำอธิบาย |
|--------|------|----------|
| GET | `/status` | สถานะบัญชี |
| POST | `/cycle` | รันรอบตัดสินใจ |
| GET | `/performance/summary` | สถิติผลงาน |
| GET | `/history` | ประวัติการเทรด |
| POST | `/daily-summary` | ส่งสรุปประจำวัน |
| POST | `/learn/analyze` | วิเคราะห์และเรียนรู้ |
| POST | `/emergency/stop` | หยุดระบบทันที |
| POST | `/emergency/resume` | เปิดระบบใหม่ |

## หมายเหตุ

- ยังเป็น Paper mode
- Hermes เป็น Chat Interface, FastAPI เป็นตัวประมวลผล
- มี Emergency Stop + Resume
