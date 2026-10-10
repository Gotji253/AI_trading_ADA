"""
Telegram notification helper.
Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
"""

import os
from typing import Optional

import requests


class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)

    def send(self, text: str, parse_mode: Optional[str] = None) -> bool:
        if not self.enabled:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text[:4000],  # Telegram limit
            "disable_web_page_preview": True,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        try:
            r = requests.post(url, json=payload, timeout=15)
            return r.status_code == 200
        except Exception:
            return False

    def send_alert(self, title: str, body: str) -> bool:
        msg = f"*{title}*\n{body}"
        return self.send(msg, parse_mode="Markdown")


def main():
    n = TelegramNotifier()
    print("Enabled:", n.enabled)
    if n.enabled:
        n.send("Test message from AI_trading_ADA")


if __name__ == "__main__":
    main()
