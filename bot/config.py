"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    bot_token: str
    admin_user_id: int
    fernet_key: str
    database_path: str = "data/bot.db"
    log_level: str = "INFO"



def load_settings() -> Settings:
    """Load and validate settings from environment variables."""
    token = os.getenv("BOT_TOKEN")
    admin_user_id = os.getenv("ADMIN_USER_ID")
    fernet_key = os.getenv("FERNET_KEY")

    if not token:
        raise ValueError("BOT_TOKEN is required")
    if not admin_user_id:
        raise ValueError("ADMIN_USER_ID is required")
    if not fernet_key:
        raise ValueError("FERNET_KEY is required")

    return Settings(
        bot_token=token,
        admin_user_id=int(admin_user_id),
        fernet_key=fernet_key,
        database_path=os.getenv("DATABASE_PATH", "data/bot.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
