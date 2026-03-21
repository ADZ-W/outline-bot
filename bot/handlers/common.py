"""Общие обработчики."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from ..keyboards import MAIN_MENU

router = Router(name="common")


@router.message(F.text == "/start")
async def start(message: Message) -> None:
    """Показать главное меню."""
    await message.answer("Бот управления Outline запущен.", reply_markup=MAIN_MENU)


@router.callback_query(F.data == "main")
async def main_menu(call: CallbackQuery) -> None:
    """Вернуться в главное меню."""
    await call.message.edit_text("Главное меню", reply_markup=MAIN_MENU)
    await call.answer()


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery) -> None:
    """Пустой callback для пагинации."""
    await call.answer()
