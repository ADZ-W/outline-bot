"""Application entrypoint."""

from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import load_settings
from .handlers import get_root_router
from .logging_config import configure_logging
from .middlewares.admin import AdminOnlyMiddleware
from .services.database import ServerRepository
from .services.encryption import EncryptionService
from .services.outline_service import OutlineService


async def run() -> None:
    """Create and run telegram bot."""
    settings = load_settings()
    configure_logging(settings.log_level)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    repo = ServerRepository(settings.database_path)
    encryption = EncryptionService(settings.fernet_key)
    outline = OutlineService(repo=repo, encryption=encryption)

    root_router = get_root_router()
    root_router.message.middleware(AdminOnlyMiddleware(settings.admin_user_id))
    root_router.callback_query.middleware(AdminOnlyMiddleware(settings.admin_user_id))

    dp.include_router(root_router)
    dp["repo"] = repo
    dp["encryption"] = encryption
    dp["outline"] = outline

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
