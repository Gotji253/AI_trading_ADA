# Market Analysis Framework (3 Dimensions)

## 1. Technical Analysis (Multi-TF)

| Timeframe | บทบาท |
|-----------|--------|
| **4h** | Macro Trend — EMA 20/50/200, Major S/R, Bullish/Bearish Bias |
| **1h** | Intermediate Structure — Consolidation, RSI, MACD |
| **15m** | Execution Trigger — Rejection at levels, Volume confirmation |

## 2. Fundamental & On-Chain (Koios)

- Chain tip, epoch info
- Network health (ช่วยกรอง Panic Sell เทียม)

## 3. Sentiment & News

- News articles + simple keyword sentiment
- ปรับ Regime เมื่อ sentiment สุดขั้ว

## การใช้งาน

```bash
# ผ่าน Alpha (3-dimension)
curl http://localhost:8000/alpha

# หรือดูผลวิเคราะห์เต็ม
python -c "
from src.analysis.market_analyzer import MarketAnalyzer
import json
a = MarketAnalyzer()
print(json.dumps(a.analyze(), indent=2, ensure_ascii=False))
"
```

## Overall Bias

ระบบรวม Technical + Sentiment + On-chain health เป็น
- `bullish` / `bearish` / `neutral`
