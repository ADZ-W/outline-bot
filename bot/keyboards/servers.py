"""Server-related keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.services.models import Server


def servers_keyboard(servers: list[Server]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{server.id} | {server.name}", callback_data=f"servers:open:{server.id}")]
        for server in servers
    ]
    rows.append([InlineKeyboardButton(text="➕ Add server", callback_data="servers:add")])
    rows.append([InlineKeyboardButton(text="⬅️ Main", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def server_menu_keyboard(server_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Create access key", callback_data=f"keys:create:{server_id}")],
            [InlineKeyboardButton(text="📋 List access keys", callback_data=f"keys:list:{server_id}:1")],
            [InlineKeyboardButton(text="✏️ Rename server", callback_data=f"servers:rename:{server_id}")],
            [InlineKeyboardButton(text="🗑 Delete server", callback_data=f"servers:delete:{server_id}")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="servers:list")],
        ]
    )
