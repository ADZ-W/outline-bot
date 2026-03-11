"""Dataclasses used across services and handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Server:
    """Stored Outline server entity."""

    id: int
    name: str
    api_url: str
    api_secret_encrypted: str
    created_at: datetime


@dataclass(slots=True)
class OutlineKey:
    """Outline access key abstraction."""

    id: str
    name: str
    access_url: str
    used_bytes: int | None = None
    data_limit_bytes: int | None = None

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "OutlineKey":
        """Build key model from Outline API response."""
        return cls(
            id=str(payload.get("id", "")),
            name=payload.get("name") or "Unnamed",
            access_url=payload.get("accessUrl", ""),
            used_bytes=(payload.get("usedBytes") if isinstance(payload.get("usedBytes"), int) else None),
            data_limit_bytes=(
                payload.get("dataLimit", {}).get("bytes")
                if isinstance(payload.get("dataLimit"), dict)
                else None
            ),
        )
