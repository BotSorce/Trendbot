"""Normalized trend data shared by source adapters, storage, and Telegram."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class TrendItem:
    """One normalized trend from an upstream provider."""

    source: str
    country_code: str
    title: str
    url: str
    summary: str = ""
    metric: str = ""
    metric_value: float | None = None
    position: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize the item for Redis JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TrendItem":
        """Rebuild an item read from Redis JSON storage."""
        return cls(**value)
