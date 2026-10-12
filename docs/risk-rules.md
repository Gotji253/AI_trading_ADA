# Risk Management Rules (Improved)

## กฎหลัก

| กฎ | ค่าเริ่มต้น | คำอธิบาย |
|-----|-----------|----------|
| Risk per Trade | 1.5% | ความเสี่ยงสูงสุดต่อไม้ |
| Daily Loss Limit | 4% | หยุดเทรดใหม่ในวันนั้น |
| Max Drawdown Hard Stop | 12% | เข้า Quarantine Mode |
| Max Open Risk | 3% | จำกัดความเสี่ยงรวม |
| **Consecutive Loss Limit** | **4 ครั้ง** | หยุดชั่วคราว (เชิงรุก) |
| **Cooldown** | **20 นาที** | หลังขาดทุนติด (เชิงรุก) |

## โหมด Cooldown

ตั้งเป็นแบบ **เชิงรุก** (ให้โอกาสมากขึ้น แต่ยังมีระยะพัก)

| โหมด | Consecutive Loss | Cooldown |
|------|------------------|----------|
| อนุรักษ์นิยม | 2 | 60–120 นาที |
| สมดุล | 3 | 30–60 นาที |
| **เชิงรุก** | **4** | **20 นาที** |

## ค่าที่ปรับได้ใน `.env`

```bash
CONSECUTIVE_LOSS_LIMIT=4
LOSS_COOLDOWN_MINUTES=20
```
