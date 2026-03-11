"""Main menu keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_MENU = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📡 Servers", callback_data="servers:list")],
        [InlineKeyboardButton(text="➕ Add server", callback_data="servers:add")],
    ]
)
