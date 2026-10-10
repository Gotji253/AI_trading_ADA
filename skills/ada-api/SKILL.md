---
name: ada-api
description: Control the ADA Multi-Agent system via FastAPI. Use to run trading cycles, check status, get performance, trigger learning, or emergency stop.
version: 1.0.0
author: AI_trading_ADA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ADA, FastAPI, Multi-Agent, Trading]
    category: finance
    requires_toolsets: [terminal]
---

# ADA FastAPI Skill

Hermes ใช้ skill นี้เพื่อสั่งงานระบบ Multi-Agent ผ่าน HTTP API

## Prerequisites

FastAPI server ต้องรันอยู่:
```bash
uvicorn src.api.main:app --port 8000
```

## Commands (via terminal + curl)

### ดูสถานะ
```bash
curl -s http://localhost:8000/status
```

### รันรอบตัดสินใจ (Alpha → Risk → Execution)
```bash
curl -s -X POST http://localhost:8000/cycle
```

### สรุปผลงาน
```bash
curl -s http://localhost:8000/performance/summary
```

### วิเคราะห์และเรียนรู้
```bash
curl -s -X POST http://localhost:8000/learn/analyze
```

### Emergency Stop (ปิดทุกตำแหน่ง + หยุดเทรด)
```bash
curl -s -X POST http://localhost:8000/emergency/stop
```

## Procedure

1. ใช้ `terminal` tool รัน curl ตามคำสั่งข้างบน
2. อ่าน JSON response
3. สรุปเป็นภาษาไทยให้ผู้ใช้เข้าใจง่าย
4. หากเป็น emergency stop ให้ยืนยันว่าระบบถูกหยุดแล้ว

## Safety

- Paper mode only
- Emergency stop ปิดตำแหน่งทันทีและหยุดการเทรดใหม่
