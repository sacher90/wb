"""Persistent storage for the latest analytics report."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class StoredReport:
    fetched_at: datetime
    data: List[Dict[str, Any]]


class FileStorage:
    """Serialize the most recent report to disk."""

    def __init__(self, path: Path) -> None:
        self._path = path
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Optional[StoredReport]:
        if not self._path.exists():
            return None
        with self._path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        fetched_at = datetime.fromisoformat(payload["fetched_at"])
        data = payload["data"]
        return StoredReport(fetched_at=fetched_at, data=data)

    def save(self, report: List[Dict[str, Any]], fetched_at: datetime) -> None:
        payload = {
            "fetched_at": fetched_at.isoformat(),
            "data": report,
        }
        with self._path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)


__all__ = ["StoredReport", "FileStorage"]
