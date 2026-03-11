"""Обработчики управления серверами."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..keyboards import MAIN_MENU, server_menu_keyboard, servers_keyboard
from ..services.database import ServerRepository
from ..services.encryption import EncryptionService
from ..services.outline_api import OutlineAPI, OutlineAPIError

from .states import ServerStates

logger = logging.getLogger(__name__)
router = Router(name="servers")


@router.callback_query(F.data == "servers:list")
async def list_servers(call: CallbackQuery, repo: ServerRepository) -> None:
    servers = repo.list_servers()
    text = "Выберите сервер:" if servers else "Серверов пока нет. Добавьте первый."
    await call.message.edit_text(text, reply_markup=servers_keyboard(servers))
    await call.answer()


@router.callback_query(F.data == "servers:add")
async def add_server_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ServerStates.adding_name)
    await call.message.answer("Введите имя сервера:")
    await call.answer()


@router.message(ServerStates.adding_name)
async def add_server_name(message: Message, state: FSMContext) -> None:
    await state.update_data(server_name=message.text.strip())
    await state.set_state(ServerStates.adding_api_url)
    await message.answer("Вставьте apiUrl из Outline (из access.txt/Manager):")


@router.message(ServerStates.adding_api_url)
async def add_server_finish(
    message: Message,
    state: FSMContext,
    repo: ServerRepository,
    encryption: EncryptionService,
) -> None:
    api_url = message.text.strip()
    if not api_url.startswith("http"):
        await message.answer("Неверный apiUrl. Пример: https://1.2.3.4:1234/UNIQUE_TOKEN")
        return

    try:
        OutlineAPI(api_url=api_url).list_keys()
    except OutlineAPIError as exc:
        await message.answer(f"Не удалось подключиться к Outline API: {exc}")
        return

    encrypted_secret = encryption.encrypt(api_url)
    data = await state.get_data()
    server_name = data["server_name"]
    server_id = repo.create_server(name=server_name, api_url=api_url, api_secret_encrypted=encrypted_secret)

    logger.info("server added id=%s name=%s", server_id, server_name)
    await state.clear()
    await message.answer(f"Сервер «{server_name}» добавлен.", reply_markup=MAIN_MENU)


@router.callback_query(F.data.startswith("servers:open:"))
async def open_server(call: CallbackQuery, repo: ServerRepository) -> None:
    server_id = int(call.data.split(":")[2])
    server = repo.get_server(server_id)
    if not server:
        await call.answer("Сервер не найден", show_alert=True)
        return

    await call.message.edit_text(
        f"Сервер: {server.name}",
        reply_markup=server_menu_keyboard(server_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("servers:rename:"))
async def rename_server_start(call: CallbackQuery, state: FSMContext) -> None:
    server_id = int(call.data.split(":")[2])
    await state.set_state(ServerStates.renaming)
    await state.update_data(server_id=server_id)
    await call.message.answer("Введите новое имя сервера:")
    await call.answer()


@router.message(ServerStates.renaming)
async def rename_server_finish(message: Message, state: FSMContext, repo: ServerRepository) -> None:
    data = await state.get_data()
    server_id = int(data["server_id"])
    repo.rename_server(server_id, message.text.strip())
    await state.clear()
    await message.answer("Сервер переименован.", reply_markup=server_menu_keyboard(server_id))


@router.callback_query(F.data.startswith("servers:delete:"))
async def delete_server(call: CallbackQuery, repo: ServerRepository) -> None:
    server_id = int(call.data.split(":")[2])
    repo.delete_server(server_id)
    logger.info("server deleted id=%s", server_id)
    await call.message.edit_text("Сервер удалён.", reply_markup=MAIN_MENU)
    await call.answer()
