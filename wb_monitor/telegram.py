"""Simple Telegram helper."""
from __future__ import annotations

import logging
from typing import Iterable, Optional, Tuple

import requests

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_ids: Iterable[str]) -> None:
        self._bot_token = bot_token
        normalized_ids = [chat_id.strip() for chat_id in chat_ids if chat_id.strip()]
        if not normalized_ids:
            raise ValueError("At least one chat ID must be provided")
        self._chat_ids: Tuple[str, ...] = tuple(normalized_ids)
        self._base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text: str, parse_mode: Optional[str] = None) -> None:
        for chat_id in self._chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            }
            if parse_mode:
                payload["parse_mode"] = parse_mode

            LOGGER.debug("Sending Telegram message to %s", chat_id)
            response = requests.post(
                f"{self._base_url}/sendMessage",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()


__all__ = ["TelegramNotifier"]
