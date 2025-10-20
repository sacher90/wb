"""Entry point for running the analytics monitor."""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .analytics_client import AnalyticsClient
from .config import Settings
from .reporting import diff_reports, render_message
from .storage import FileStorage
from .telegram import TelegramNotifier

LOG_LEVELS = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING}


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wildberries analytics monitor")
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Fetch data once and exit instead of running continuously.",
    )
    parser.add_argument(
        "--metrics-aliases",
        type=Path,
        help="Path to a JSON file with metric aliases for friendlier Telegram messages.",
    )
    parser.add_argument(
        "--log-level",
        choices=list(LOG_LEVELS.keys()),
        default="info",
        help="Logging level",
    )
    return parser.parse_args(argv)


def load_metric_aliases(path: Optional[Path]) -> Dict[str, str]:
    if not path:
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_once(settings: Settings, metric_aliases: Dict[str, str]) -> None:
    logging.getLogger(__name__).debug("Starting single run with %s", settings)

    client = AnalyticsClient(settings.wb_api_url, settings.wb_api_token)
    storage = FileStorage(settings.state_file)
    telegram = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)

    fetched_at = datetime.utcnow()
    report = client.fetch_report()
    previous = storage.load()
    changes = diff_reports(
        previous.data if previous else None,
        report,
        key_field=settings.key_field,
        metrics=settings.tracked_metrics,
    )
    message = render_message(changes, fetched_at=fetched_at.isoformat(), metrics_display=metric_aliases)

    telegram.send_message(message)
    storage.save(report, fetched_at)


def run(settings: Settings, run_once_flag: bool, metric_aliases: Dict[str, str]) -> None:
    if run_once_flag:
        run_once(settings, metric_aliases)
        return

    while True:
        try:
            run_once(settings, metric_aliases)
        except Exception as exc:  # pragma: no cover - defensive logging
            logging.exception("Failed to process analytics cycle: %s", exc)
        time.sleep(settings.interval_seconds)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=LOG_LEVELS.get(level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def cli(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    configure_logging(args.log_level)
    settings = Settings.from_env()
    metric_aliases = load_metric_aliases(args.metrics_aliases)
    run(settings, args.run_once, metric_aliases)


if __name__ == "__main__":
    cli(sys.argv[1:])
