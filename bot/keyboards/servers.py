"""Клавиатуры раздела серверов."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..services.models import Server


def servers_keyboard(servers: list[Server]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{server.id} | {server.name}", callback_data=f"servers:open:{server.id}")]
        for server in servers
    ]
    rows.append([InlineKeyboardButton(text="➕ Добавить сервер", callback_data="servers:add")])
    rows.append([InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def server_menu_keyboard(server_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать ключ", callback_data=f"keys:create:{server_id}")],
            [InlineKeyboardButton(text="📋 Список ключей", callback_data=f"keys:list:{server_id}:1")],
            [InlineKeyboardButton(text="✏️ Переименовать сервер", callback_data=f"servers:rename:{server_id}")],
            [InlineKeyboardButton(text="🗑 Удалить сервер", callback_data=f"servers:delete:{server_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="servers:list")],
        ]
    )
