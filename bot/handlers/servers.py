"""Server management handlers."""

from __future__ import annotations

import logging
from urllib.parse import urlsplit, urlunsplit

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import MAIN_MENU, server_menu_keyboard, servers_keyboard
from bot.services.database import ServerRepository
from bot.services.encryption import EncryptionService
from bot.services.outline_api import OutlineAPI, OutlineAPIError

from .states import ServerStates

logger = logging.getLogger(__name__)
router = Router(name="servers")


@router.callback_query(F.data == "servers:list")
async def list_servers(call: CallbackQuery, repo: ServerRepository) -> None:
    servers = repo.list_servers()
    text = "Select server:" if servers else "No servers yet. Add one."
    await call.message.edit_text(text, reply_markup=servers_keyboard(servers))
    await call.answer()


@router.callback_query(F.data == "servers:add")
async def add_server_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ServerStates.adding_name)
    await call.message.answer("Send server name:")
    await call.answer()


@router.message(ServerStates.adding_name)
async def add_server_name(message: Message, state: FSMContext) -> None:
    await state.update_data(server_name=message.text.strip())
    await state.set_state(ServerStates.adding_api_url)
    await message.answer("Paste Outline API URL (secret key URL):")


@router.message(ServerStates.adding_api_url)
async def add_server_finish(
    message: Message,
    state: FSMContext,
    repo: ServerRepository,
    encryption: EncryptionService,
) -> None:
    secret_url = message.text.strip()
    parsed = urlsplit(secret_url)

    if parsed.scheme not in {"http", "https"} or not parsed.hostname or not parsed.username:
        await message.answer("Invalid Outline secret URL format.")
        return

    api_url = urlunsplit((parsed.scheme, parsed.hostname + (f":{parsed.port}" if parsed.port else ""), "", "", ""))

    try:
        OutlineAPI(secret_url).list_keys()
    except OutlineAPIError as exc:
        await message.answer(f"Unable to connect to Outline API: {exc}")
        return

    encrypted_secret = encryption.encrypt(secret_url)
    data = await state.get_data()
    server_name = data["server_name"]
    server_id = repo.create_server(name=server_name, api_url=api_url, api_secret_encrypted=encrypted_secret)

    logger.info("server added id=%s name=%s", server_id, server_name)
    await state.clear()
    await message.answer(f"Server '{server_name}' added.", reply_markup=MAIN_MENU)


@router.callback_query(F.data.startswith("servers:open:"))
async def open_server(call: CallbackQuery, repo: ServerRepository) -> None:
    server_id = int(call.data.split(":")[2])
    server = repo.get_server(server_id)
    if not server:
        await call.answer("Server not found", show_alert=True)
        return

    await call.message.edit_text(
        f"Server: {server.name}\nAPI Host: {server.api_url}",
        reply_markup=server_menu_keyboard(server_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("servers:rename:"))
async def rename_server_start(call: CallbackQuery, state: FSMContext) -> None:
    server_id = int(call.data.split(":")[2])
    await state.set_state(ServerStates.renaming)
    await state.update_data(server_id=server_id)
    await call.message.answer("Send new server name:")
    await call.answer()


@router.message(ServerStates.renaming)
async def rename_server_finish(message: Message, state: FSMContext, repo: ServerRepository) -> None:
    data = await state.get_data()
    server_id = int(data["server_id"])
    repo.rename_server(server_id, message.text.strip())
    await state.clear()
    await message.answer("Server renamed.", reply_markup=server_menu_keyboard(server_id))


@router.callback_query(F.data.startswith("servers:delete:"))
async def delete_server(call: CallbackQuery, repo: ServerRepository) -> None:
    server_id = int(call.data.split(":")[2])
    repo.delete_server(server_id)
    logger.info("server deleted id=%s", server_id)
    await call.message.edit_text("Server deleted.", reply_markup=MAIN_MENU)
    await call.answer()
