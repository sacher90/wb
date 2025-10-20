"""Diffing utilities for analytics reports."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass(slots=True)
class MetricChange:
    item_id: str
    metric: str
    previous: Optional[float]
    current: Optional[float]

    @property
    def delta(self) -> Optional[float]:
        if self.previous is None or self.current is None:
            return None
        return self.current - self.previous


@dataclass(slots=True)
class ItemChange:
    item_id: str
    created: bool = False
    removed: bool = False
    metrics: List[MetricChange] | None = None


def build_index(report: List[Dict[str, Any]], key_field: str) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for row in report:
        key = str(row.get(key_field))
        if key == "None":
            continue
        index[key] = row
    return index


def diff_reports(
    previous: Optional[List[Dict[str, Any]]],
    current: List[Dict[str, Any]],
    key_field: str,
    metrics: Iterable[str],
) -> List[ItemChange]:
    previous_index = build_index(previous or [], key_field)
    current_index = build_index(current, key_field)

    changes: List[ItemChange] = []
    for item_id, current_row in current_index.items():
        previous_row = previous_index.get(item_id)
        if previous_row is None:
            changes.append(ItemChange(item_id=item_id, created=True))
            continue

        metric_changes: List[MetricChange] = []
        for metric in metrics:
            current_value = _to_float(current_row.get(metric))
            previous_value = _to_float(previous_row.get(metric))
            if current_value is None and previous_value is None:
                continue
            if current_value == previous_value:
                continue
            metric_changes.append(
                MetricChange(
                    item_id=item_id,
                    metric=metric,
                    previous=previous_value,
                    current=current_value,
                )
            )
        if metric_changes:
            changes.append(ItemChange(item_id=item_id, metrics=metric_changes))

    for item_id in previous_index.keys() - current_index.keys():
        changes.append(ItemChange(item_id=item_id, removed=True))

    return changes


def render_message(
    changes: List[ItemChange],
    fetched_at: str,
    metrics_display: Dict[str, str] | None = None,
) -> str:
    if not changes:
        return (
            "Обновление Wildberries на {fetched_at}. Изменений по выбранным метрикам нет.".format(
                fetched_at=fetched_at
            )
        )

    parts = [f"Обновление Wildberries на {fetched_at}. Изменения:" ]
    for change in changes:
        if change.created:
            parts.append(f"• Новый товар {change.item_id}")
            continue
        if change.removed:
            parts.append(f"• Товар {change.item_id} больше не присутствует в отчете")
            continue
        assert change.metrics is not None
        parts.append(f"• Товар {change.item_id}:")
        for metric_change in change.metrics:
            metric_name = (
                metrics_display.get(metric_change.metric, metric_change.metric)
                if metrics_display
                else metric_change.metric
            )
            previous = _format_optional(metric_change.previous)
            current = _format_optional(metric_change.current)
            delta = _format_optional(metric_change.delta, signed=True)
            parts.append(
                f"    - {metric_name}: {current} (было {previous}, изменение {delta})"
            )

    return "\n".join(parts)


def _format_optional(value: Optional[float], signed: bool = False) -> str:
    if value is None:
        return "нет данных"
    if signed:
        return f"{value:+.2f}"
    return f"{value:.2f}"


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


__all__ = [
    "MetricChange",
    "ItemChange",
    "diff_reports",
    "render_message",
]
