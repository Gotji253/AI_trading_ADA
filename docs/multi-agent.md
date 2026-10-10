# Multi-Agent Architecture (via FastAPI)

## Agents

| Agent | บทบาท |
|-------|--------|
| **Alpha_Agent** | หาจังหวะเทรด (Multi-TF + S/R + technical) |
| **Risk_Agent** | คุมขนาดไม้, Drawdown, Daily loss, Position sizing |
| **Execution_Agent** | จำลองเทรด (Paper) / ตรวจ SL-TP |
| **Manager_Agent** | ประสานงานทั้งหมด ตัดสินใจเป็นรอบ |

## รัน FastAPI

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

## Endpoints

| Method | Path | คำอธิบาย |
|--------|------|----------|
| GET | `/status` | สถานะบัญชี paper |
| POST | `/cycle` | รันหนึ่งรอบ Alpha → Risk → Execution |
| GET | `/alpha` | ดูสัญญาณจาก Alpha_Agent |
| GET | `/risk?signal=buy&price=0.45` | ตรวจความเสี่ยงจาก Risk_Agent |

## ตัวอย่างการทำงาน

```bash
# ดูสถานะ
curl http://localhost:8000/status

# รันรอบตัดสินใจ
curl -X POST http://localhost:8000/cycle
```

## หมายเหตุ

- Alpha หาจังหวะ
- Risk อนุมัติหรือปฏิเสธ
- Execution ทำงานจริงเฉพาะ paper
- Manager ประสานงานทั้งหมด
