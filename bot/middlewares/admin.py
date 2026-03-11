"""Admin-only access middleware."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class AdminOnlyMiddleware(BaseMiddleware):
    """Allow access only to a single configured Telegram user id."""

    def __init__(self, admin_user_id: int) -> None:
        self._admin_user_id = admin_user_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        if isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id != self._admin_user_id:
            if isinstance(event, Message):
                await event.answer("Доступ запрещён.")
                return None
            if isinstance(event, CallbackQuery):
                await event.answer("Доступ запрещён.", show_alert=True)
                return None

        return await handler(event, data)
