"""Клавиатура главного меню."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_MENU = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📡 Серверы", callback_data="servers:list")],
        [InlineKeyboardButton(text="➕ Добавить сервер", callback_data="servers:add")],
    ]
)
