# AI_trading_ADA

Hermes Agent for **Cardano (ADA) only**  
Technical signals + **AI Analysis** + Paper Trading.

## Quick Start

```bash
git clone https://github.com/Gotji253/AI_trading_ADA.git
cd AI_trading_ADA
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add BINANCE keys and OPENROUTER_API_KEY (or OPENAI_API_KEY)
```

## Commands

```bash
python -m src.cli status
python -m src.cli ada-price
python -m src.cli ada-signal --interval 1h
python -m src.cli ai-analyze --interval 1h      # AI analysis (needs LLM key)
python -m src.cli paper-status
python -m src.cli paper-auto --interval 1h
python -m src.cli paper-history
```

## AI Analysis

`ai-analyze` sends the technical data to an LLM and returns a structured Thai analysis:
- สถานะการณ์ทางเทคนิค
- ทัศนคติเชิงสัญญาณ
- ระดับความเสี่ยง
- แนะนำสำหรับนักเทรดระยะสั้น

## Paper Trading

Virtual 10,000 USDT. No real money.

## Hermes Skill

```bash
mkdir -p ~/.hermes/skills/finance
cp -r skills/ada-trader ~/.hermes/skills/finance/
```

## Safety

Paper mode only. Live trading is not implemented.
