"""
AI Analysis for ADA.
Supports single timeframe or multi-timeframe summary.
"""

import json
from typing import Dict, Any, Optional

import requests

from src.config import get_config
from src.signals.ada_signals import ADASignalGenerator
from src.signals.multi_tf import MultiTimeframeAnalyzer


class ADAAIAnalyzer:
    def __init__(self, model: Optional[str] = None):
        self.cfg = get_config()
        self.signal_gen = ADASignalGenerator()
        self.multi = MultiTimeframeAnalyzer()
        self.model = model or self.cfg.OPENROUTER_MODEL

    def _call_llm(self, prompt: str) -> str:
        if self.cfg.OPENROUTER_API_KEY:
            return self._openrouter(prompt)
        if self.cfg.OPENAI_API_KEY:
            return self._openai(prompt)
        return "Error: No OPENROUTER_API_KEY or OPENAI_API_KEY set in .env"

    def _openrouter(self, prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.cfg.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Gotji253/AI_trading_ADA",
            "X-Title": "AI_trading_ADA",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 900,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _openai(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.cfg.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 900,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def analyze(self, interval: str = "1h", multi: bool = False) -> Dict[str, Any]:
        if multi:
            data = self.multi.analyze()
            prompt_data = data
        else:
            data = self.signal_gen.generate(interval=interval)
            prompt_data = data

        if data.get("status") != "ok":
            return data

        prompt = f"""You are a professional crypto analyst focused only on Cardano (ADA).

Data:
{json.dumps(prompt_data, indent=2, ensure_ascii=False)}

Provide a concise analysis in Thai:
1. สรุปสถานะการณ์ (2-3 ประโยค)
2. Timeframe ไหนแข็งแกร่งที่สุดและเหตุผล (ถ้าเป็น multi-tf)
3. ทัศนคติเชิงสัญญาณ (buy/sell/hold) พร้อมเหตุผล
4. ระดับความเสี่ยงและโอกาส
5. แนะนำสำหรับนักเทรดระยะสั้น

เป็นการวิเคราะห์เท่านั้น ไม่ใช่คำแนะนำทางการเงิน"""

        ai_text = self._call_llm(prompt)

        return {
            "status": "ok",
            "symbol": "ADA",
            "model_used": self.model,
            "data": data,
            "ai_analysis": ai_text,
            "trading_mode": self.cfg.TRADING_MODE,
        }


def main():
    analyzer = ADAAIAnalyzer()
    result = analyzer.analyze("1h", multi=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
