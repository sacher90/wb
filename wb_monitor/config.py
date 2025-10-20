"""Configuration helpers for the Wildberries analytics monitor."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import os


@dataclass(slots=True)
class Settings:
    """Runtime configuration for the monitor."""

    wb_api_token: str
    telegram_bot_token: str
    telegram_chat_id: str
    interval_seconds: int = 3600
    wb_api_url: str = (
        "https://statistics-api.wildberries.ru/api/v1/supplier/analytics"  # default Analytics API
    )
    state_file: Path = Path("state/latest_report.json")
    tracked_metrics: List[str] = field(
        default_factory=lambda: ["ordersCount", "ordersSum", "buyoutsCount", "revenue"]
    )
    key_field: str = "nmId"

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""

        wb_api_token = _require_env("WB_API_TOKEN")
        telegram_bot_token = _require_env("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = _require_env("TELEGRAM_CHAT_ID")

        interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "3600"))
        wb_api_url = os.getenv(
            "WB_ANALYTICS_URL",
            "https://statistics-api.wildberries.ru/api/v1/supplier/analytics",
        )
        state_file = Path(os.getenv("STATE_FILE", "state/latest_report.json"))
        tracked_metrics = _split_env_list(
            os.getenv("TRACKED_METRICS", "ordersCount,ordersSum,buyoutsCount,revenue")
        )
        key_field = os.getenv("TRACKED_KEY_FIELD", "nmId")

        return cls(
            wb_api_token=wb_api_token,
            telegram_bot_token=telegram_bot_token,
            telegram_chat_id=telegram_chat_id,
            interval_seconds=interval_seconds,
            wb_api_url=wb_api_url,
            state_file=state_file,
            tracked_metrics=tracked_metrics,
            key_field=key_field,
        )


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def _split_env_list(raw: str | None) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


__all__ = ["Settings"]
