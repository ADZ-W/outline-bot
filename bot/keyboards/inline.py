"""Inline keyboard builders."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.services.models import OutlineKey, Server


MAIN_MENU = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📡 Servers", callback_data="servers:list")],
        [InlineKeyboardButton(text="➕ Add server", callback_data="servers:add")],
    ]
)


def servers_keyboard(servers: list[Server]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"{srv.id} | {srv.name}", callback_data=f"servers:open:{srv.id}")] for srv in servers]
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


def keys_keyboard(server_id: int, keys: list[OutlineKey], page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for key in keys:
        rows.append([InlineKeyboardButton(text=f"{key.id} | {key.name}", callback_data=f"keys:open:{server_id}:{key.id}")])

    nav: list[InlineKeyboardButton] = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"keys:list:{server_id}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{max(total_pages, 1)}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"keys:list:{server_id}:{page + 1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text="⬅️ Back", callback_data=f"servers:open:{server_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def key_menu_keyboard(server_id: int, key_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Show key", callback_data=f"keys:show:{server_id}:{key_id}")],
            [InlineKeyboardButton(text="✏️ Rename key", callback_data=f"keys:rename:{server_id}:{key_id}")],
            [InlineKeyboardButton(text="📉 Set data limit", callback_data=f"keys:set_limit:{server_id}:{key_id}")],
            [InlineKeyboardButton(text="♻️ Remove data limit", callback_data=f"keys:remove_limit:{server_id}:{key_id}")],
            [InlineKeyboardButton(text="🗑 Delete key", callback_data=f"keys:delete:{server_id}:{key_id}")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data=f"keys:list:{server_id}:1")],
        ]
    )
