---
name: ada-api
description: Control the ADA Multi-Agent trading system via FastAPI. Run cycles, check status, performance, history, learning, or emergency stop/resume. Just put API keys in .env and run.
version: 1.2.0
author: AI_trading_ADA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ADA, FastAPI, Multi-Agent, Trading, Hermes]
    category: finance
    requires_toolsets: [terminal]
---

# ADA FastAPI Skill (Ready to Run)

Hermes ใช้ skill นี้เพื่อสั่งงานระบบ AI_trading_ADA ผ่าน HTTP API

## การติดตั้งแบบพร้อมใช้งาน (ครั้งเดียว)

```bash
# 1. คัดลอกและติดตั้ง skill
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-api ~/.hermes/skills/finance/

# 2. ใส่ API key ใน .env (ถ้ายังไม่ได้ใส่)
cp .env.example .env
# แก้ไข OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# 3. รัน FastAPI server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## การใช้งานใน Hermes

พิมพ์ `/ada-api` แล้วตามด้วยคำสั่ง เช่น:

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

## คำสั่งที่รองรับ

| คำสั่ง | Endpoint |
|--------|----------|
| ดูสถานะ / status | `GET /status` |
| รันรอบ / cycle | `POST /cycle` |
| สรุปผล / performance | `GET /performance/summary` |
| ประวัติ / history | `GET /history` |
| สรุปประจำวัน / daily | `POST /daily-summary` |
| เรียนรู้ / learn | `POST /learn/analyze` |
| emergency stop | `POST /emergency/stop` |
| resume | `POST /emergency/resume` |

## Procedure

1. ใช้ `terminal` tool รัน curl ไปที่ endpoint ที่เกี่ยวข้อง
2. Base URL คือ `http://localhost:8000` (หรือตั้ง `ADA_API_BASE` ถ้าต่างกัน)
3. อ่าน JSON response แล้วสรุปเป็นภาษาไทยให้ผู้ใช้เข้าใจง่าย
4. ถ้าเซิร์ฟเวอร์ไม่รัน ให้บอกผู้ใช้รัน `uvicorn src.api.main:app --port 8000`
5. ถ้าเป็น emergency stop ให้ยืนยันว่าระบบถูกหยุดแล้ว

## Safety

- เป็น Paper mode เท่านั้น
- Emergency stop ปิดตำแหน่งทั้งหมดและหยุดการเทรดใหม่
- ใช้ resume เพื่อเปิดการเทรดใหม่
