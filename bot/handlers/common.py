"""Common handlers."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards import MAIN_MENU

router = Router(name="common")


@router.message(F.text == "/start")
async def start(message: Message) -> None:
    """Show main menu."""
    await message.answer("Outline manager is ready.", reply_markup=MAIN_MENU)


@router.callback_query(F.data == "main")
async def main_menu(call: CallbackQuery) -> None:
    """Go to main menu."""
    await call.message.edit_text("Main menu", reply_markup=MAIN_MENU)
    await call.answer()


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery) -> None:
    """Ignore no-op callbacks."""
    await call.answer()
