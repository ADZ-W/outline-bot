"""Formatting helpers for Telegram output."""

from __future__ import annotations


def format_bytes(value: int | None) -> str:
    """Human readable bytes formatting."""
    if value is None:
        return "unlimited"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{value} B"
