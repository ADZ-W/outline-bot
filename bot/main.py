"""Application entrypoint."""

from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_settings
from bot.handlers import router
from bot.logging_config import configure_logging
from bot.services.database import ServerRepository
from bot.services.encryption import EncryptionService


async def run() -> None:
    """Create and run telegram bot."""
    settings = load_settings()
    configure_logging(settings.log_level)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    repo = ServerRepository(settings.database_path)
    encryption = EncryptionService(settings.fernet_key)

    dp.include_router(router)
    dp["repo"] = repo
    dp["encryption"] = encryption
    dp["admin_user_id"] = settings.admin_user_id

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
