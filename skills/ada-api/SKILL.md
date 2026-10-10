---
name: ada-api
description: Control the ADA Multi-Agent system via FastAPI. Run cycles, check status, get history/performance, daily summary, learning analysis, or emergency stop/resume.
version: 1.1.0
author: AI_trading_ADA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ADA, FastAPI, Multi-Agent, Trading, Hermes]
    category: finance
    requires_toolsets: [terminal]
---

# ADA FastAPI Skill

Hermes ใช้ skill นี้เพื่อสั่งงานระบบ Multi-Agent ผ่าน HTTP API

## Prerequisites

FastAPI server ต้องรันอยู่ที่ `http://localhost:8000` ("หรือตั้ง `ADA_API_BASE` ใน environment ถ้าต่างกัน)

```bash
uvicorn src.api.main:app --port 8000
```

## Base URL

ใช้ตัวแปรนี้ถ้าต้องการเปลี่ยน URL:
```bash
export ADA_API_BASE=http://localhost:8000
```

## Commands (via terminal + curl)

แทน `$ADA_API_BASE` ด้วยค่าจริง หรือใช้ `http://localhost:8000`

### ดูสถานะ
```bash
curl -s ${ADA_API_BASE:-http://localhost:8000}/status
```

### รันรอบตัดสินใจ (Alpha → Risk → Execution)
```bash
curl -s -X POST ${ADA_API_BASE:-http://localhost:8000}/cycle
```

### สรุปผลงาน
```bash
curl -s ${ADA_API_BASE:-http://localhost:8000}/performance/summary
```

### ประวัติการเทรด
```bash
curl -s "${ADA_API_BASE:-http://localhost:8000}/history?limit=10"
```

### สรุปประจำวัน (ส่ง Telegram)
```bash
curl -s -X POST ${ADA_API_BASE:-http://localhost:8000}/daily-summary
```

### วิเคราะห์และเรียนรู้
```bash
curl -s -X POST ${ADA_API_BASE:-http://localhost:8000}/learn/analyze
```

### Emergency Stop (ปิดทุกตำแหน่ง + หยุดเทรด)
```bash
curl -s -X POST ${ADA_API_BASE:-http://localhost:8000}/emergency/stop
```

### Resume (เปิดการเทรดใหม่)
```bash
curl -s -X POST ${ADA_API_BASE:-http://localhost:8000}/emergency/resume
```

## Procedure

1. ใช้ `terminal` tool รัน curl ตามคำสั่งข้างบน
2. ถ้า response ไม่ใช่ JSON ที่ถูกต้อง ให้บอกผู้ใช้ว่าเซิร์ฟเวอร์ไม่รัน
3. อ่าน JSON แล้วสรุปเป็นภาษาไทยให้ผู้ใช้เข้าใจง่าย
4. ถ้าเป็น emergency stop ให้ยืนยันว่าระบบถูกหยุดแล้ว
5. ถ้าต้องการ resume ให้บอกผู้ใช้ว่าเปิดการเทรดได้แล้ว

## Safety

- Paper mode only
- Emergency stop ปิดตำแหน่งทันทีและหยุดการเทรดใหม่
- ใช้ resume เพื่อเปิดการเทรดใหม่
