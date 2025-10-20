"""Client for the Wildberries Analytics API."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

LOGGER = logging.getLogger(__name__)


class AnalyticsClient:
    """Thin wrapper around the Wildberries Analytics endpoint."""

    def __init__(self, base_url: str, token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token

    def fetch_report(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch analytics data for the given period.

        If no dates are provided, Wildberries returns data for the default period
        configured on the account (usually yesterday). We fall back to requesting
        data for the last 7 days to make the report more useful.
        """

        if not date_to:
            date_to = datetime.utcnow()
        if not date_from:
            date_from = date_to - timedelta(days=7)

        params = {
            "dateFrom": date_from.strftime("%Y-%m-%d"),
            "dateTo": date_to.strftime("%Y-%m-%d"),
        }
        headers = {
            "Authorization": self._token,
            "Content-Type": "application/json",
        }

        LOGGER.debug("Requesting analytics %s with params %s", self._base_url, params)
        response = requests.get(self._base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise ValueError("Unexpected API response: expected list of analytics records")

        LOGGER.info("Fetched %d analytics rows", len(data))
        return data


__all__ = ["AnalyticsClient"]
