"""Access key-related keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.services.models import OutlineKey


def keys_keyboard(server_id: int, keys: list[OutlineKey], page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{key.id} | {key.name}", callback_data=f"keys:open:{server_id}:{key.id}")]
        for key in keys
    ]

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
