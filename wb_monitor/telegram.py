"""Simple Telegram helper."""
from __future__ import annotations

import logging
from typing import Optional

import requests

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text: str, parse_mode: Optional[str] = None) -> None:
        payload = {
            "chat_id": self._chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        LOGGER.debug("Sending Telegram message to %s", self._chat_id)
        response = requests.post(
            f"{self._base_url}/sendMessage",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()


__all__ = ["TelegramNotifier"]
