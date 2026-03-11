"""Main bot handlers for servers and keys management."""

from __future__ import annotations

import logging
from math import ceil
from urllib.parse import urlsplit, urlunsplit

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import (
    MAIN_MENU,
    key_menu_keyboard,
    keys_keyboard,
    server_menu_keyboard,
    servers_keyboard,
)
from bot.services.database import ServerRepository
from bot.services.encryption import EncryptionService
from bot.services.models import OutlineKey
from bot.services.outline_api import OutlineAPI, OutlineAPIError

from .states import KeyStates, ServerStates

logger = logging.getLogger(__name__)
router = Router()



def _is_admin(user_id: int, admin_user_id: int) -> bool:
    return user_id == admin_user_id


@router.message(F.text == "/start")
async def start(message: Message, admin_user_id: int) -> None:
    if not _is_admin(message.from_user.id, admin_user_id):
        await message.answer("Access denied.")
        return
    await message.answer("Outline manager is ready.", reply_markup=MAIN_MENU)


@router.callback_query(F.data == "main")
async def main_menu(call: CallbackQuery, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    await call.message.edit_text("Main menu", reply_markup=MAIN_MENU)
    await call.answer()


@router.callback_query(F.data == "servers:list")
async def list_servers(call: CallbackQuery, repo: ServerRepository, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    servers = repo.list_servers()
    text = "Select server:" if servers else "No servers yet. Add one."
    await call.message.edit_text(text, reply_markup=servers_keyboard(servers))
    await call.answer()


@router.callback_query(F.data == "servers:add")
async def add_server_start(call: CallbackQuery, state: FSMContext, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    await state.set_state(ServerStates.adding_name)
    await call.message.answer("Send server name:")
    await call.answer()


@router.message(ServerStates.adding_name)
async def add_server_name(message: Message, state: FSMContext, admin_user_id: int) -> None:
    if not _is_admin(message.from_user.id, admin_user_id):
        return
    await state.update_data(server_name=message.text.strip())
    await state.set_state(ServerStates.adding_api_url)
    await message.answer("Paste Outline API URL (secret URL):")


@router.message(ServerStates.adding_api_url)
async def add_server_finish(
    message: Message,
    state: FSMContext,
    repo: ServerRepository,
    encryption: EncryptionService,
    admin_user_id: int,
) -> None:
    if not _is_admin(message.from_user.id, admin_user_id):
        return

    secret_url = message.text.strip()
    if not secret_url.startswith("http"):
        await message.answer("Invalid URL, please send http(s) URL.")
        return

    parsed = urlsplit(secret_url)
    if not parsed.username or not parsed.password:
        await message.answer("Invalid Outline secret URL format.")
        return

    safe_api_url = urlunsplit((parsed.scheme, parsed.hostname + (f":{parsed.port}" if parsed.port else ""), "", "", ""))

    data = await state.get_data()
    name = data["server_name"]
    encrypted = encryption.encrypt(secret_url)
    server_id = repo.create_server(name=name, api_url=safe_api_url, api_secret_encrypted=encrypted)
    logger.info("server added id=%s name=%s", server_id, name)
    await state.clear()
    await message.answer(f"Server '{name}' added.", reply_markup=MAIN_MENU)


@router.callback_query(F.data.startswith("servers:open:"))
async def open_server(call: CallbackQuery, repo: ServerRepository, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    server_id = int(call.data.split(":")[2])
    server = repo.get_server(server_id)
    if not server:
        await call.answer("Server not found", show_alert=True)
        return
    await call.message.edit_text(f"Server: {server.name}", reply_markup=server_menu_keyboard(server_id))
    await call.answer()


@router.callback_query(F.data.startswith("servers:rename:"))
async def rename_server_start(call: CallbackQuery, state: FSMContext, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    server_id = int(call.data.split(":")[2])
    await state.set_state(ServerStates.renaming)
    await state.update_data(server_id=server_id)
    await call.message.answer("Send new server name:")
    await call.answer()


@router.message(ServerStates.renaming)
async def rename_server_finish(message: Message, state: FSMContext, repo: ServerRepository, admin_user_id: int) -> None:
    if not _is_admin(message.from_user.id, admin_user_id):
        return
    data = await state.get_data()
    server_id = int(data["server_id"])
    repo.rename_server(server_id, message.text.strip())
    await state.clear()
    await message.answer("Server renamed.", reply_markup=server_menu_keyboard(server_id))


@router.callback_query(F.data.startswith("servers:delete:"))
async def delete_server(call: CallbackQuery, repo: ServerRepository, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    server_id = int(call.data.split(":")[2])
    repo.delete_server(server_id)
    logger.info("server deleted id=%s", server_id)
    await call.message.edit_text("Server deleted.", reply_markup=MAIN_MENU)
    await call.answer()


def _get_outline_api(server_id: int, repo: ServerRepository, encryption: EncryptionService) -> OutlineAPI:
    server = repo.get_server(server_id)
    if not server:
        raise OutlineAPIError("Server not found")
    decrypted = encryption.decrypt(server.api_secret_encrypted)
    return OutlineAPI(api_url=decrypted)


@router.callback_query(F.data.startswith("keys:create:"))
async def create_key(call: CallbackQuery, repo: ServerRepository, encryption: EncryptionService, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    server_id = int(call.data.split(":")[2])
    try:
        api = _get_outline_api(server_id, repo, encryption)
        key = api.create_key()
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return
    logger.info("key created server_id=%s key_id=%s", server_id, key.id)
    await call.message.answer(f"Created key {key.id}")
    await call.answer()


@router.callback_query(F.data.startswith("keys:list:"))
async def list_keys(call: CallbackQuery, repo: ServerRepository, encryption: EncryptionService, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    _, _, server_id_s, page_s = call.data.split(":")
    server_id, page = int(server_id_s), int(page_s)
    try:
        api = _get_outline_api(server_id, repo, encryption)
        keys = api.list_keys()
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    per_page = 10
    total_pages = max(1, ceil(len(keys) / per_page))
    page = min(max(page, 1), total_pages)
    start = (page - 1) * per_page
    paginated = keys[start : start + per_page]
    await call.message.edit_text(
        f"Access keys ({len(keys)} total):",
        reply_markup=keys_keyboard(server_id, paginated, page, total_pages),
    )
    await call.answer()


@router.callback_query(F.data.startswith("keys:open:"))
async def open_key(call: CallbackQuery, repo: ServerRepository, encryption: EncryptionService, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)
    try:
        api = _get_outline_api(server_id, repo, encryption)
        key = api.get_key_info(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    text = (
        f"Name: {key.name}\n"
        f"ID: {key.id}\n"
        f"Data used: {key.used_bytes or 0} bytes\n"
        f"Data limit: {key.data_limit_bytes if key.data_limit_bytes is not None else 'unlimited'}"
    )
    await call.message.edit_text(text, reply_markup=key_menu_keyboard(server_id, key.id))
    await call.answer()


@router.callback_query(F.data.startswith("keys:show:"))
async def show_key(call: CallbackQuery, repo: ServerRepository, encryption: EncryptionService, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)
    try:
        api = _get_outline_api(server_id, repo, encryption)
        key = api.get_key_info(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return
    await call.message.answer(f"Access URL:\n{key.access_url}")
    await call.answer()


@router.callback_query(F.data.startswith("keys:rename:"))
async def rename_key_start(call: CallbackQuery, state: FSMContext, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    _, _, server_id_s, key_id = call.data.split(":")
    await state.set_state(KeyStates.renaming)
    await state.update_data(server_id=int(server_id_s), key_id=key_id)
    await call.message.answer("Send new key name:")
    await call.answer()


@router.message(KeyStates.renaming)
async def rename_key_finish(
    message: Message,
    state: FSMContext,
    repo: ServerRepository,
    encryption: EncryptionService,
    admin_user_id: int,
) -> None:
    if not _is_admin(message.from_user.id, admin_user_id):
        return
    data = await state.get_data()
    server_id, key_id = int(data["server_id"]), data["key_id"]
    try:
        api = _get_outline_api(server_id, repo, encryption)
        api.rename_key(key_id, message.text.strip())
    except OutlineAPIError as exc:
        await message.answer(str(exc))
        return
    await state.clear()
    await message.answer("Key renamed.")


@router.callback_query(F.data.startswith("keys:set_limit:"))
async def set_limit_start(call: CallbackQuery, state: FSMContext, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    _, _, server_id_s, key_id = call.data.split(":")
    await state.set_state(KeyStates.setting_limit)
    await state.update_data(server_id=int(server_id_s), key_id=key_id)
    await call.message.answer("Send data limit in GB (integer):")
    await call.answer()


@router.message(KeyStates.setting_limit)
async def set_limit_finish(
    message: Message,
    state: FSMContext,
    repo: ServerRepository,
    encryption: EncryptionService,
    admin_user_id: int,
) -> None:
    if not _is_admin(message.from_user.id, admin_user_id):
        return
    try:
        limit_gb = int(message.text.strip())
        if limit_gb <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Please send positive integer GB value.")
        return

    data = await state.get_data()
    server_id, key_id = int(data["server_id"]), data["key_id"]
    bytes_limit = limit_gb * 1024 * 1024 * 1024
    try:
        api = _get_outline_api(server_id, repo, encryption)
        api.set_data_limit(key_id, bytes_limit)
    except OutlineAPIError as exc:
        await message.answer(str(exc))
        return
    logger.info("limit changed server_id=%s key_id=%s bytes=%s", server_id, key_id, bytes_limit)
    await state.clear()
    await message.answer("Data limit updated.")


@router.callback_query(F.data.startswith("keys:remove_limit:"))
async def remove_limit(call: CallbackQuery, repo: ServerRepository, encryption: EncryptionService, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)
    try:
        api = _get_outline_api(server_id, repo, encryption)
        api.remove_data_limit(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return
    logger.info("limit changed server_id=%s key_id=%s removed=true", server_id, key_id)
    await call.message.answer("Data limit removed.")
    await call.answer()


@router.callback_query(F.data.startswith("keys:delete:"))
async def delete_key(call: CallbackQuery, repo: ServerRepository, encryption: EncryptionService, admin_user_id: int) -> None:
    if not _is_admin(call.from_user.id, admin_user_id):
        await call.answer("Access denied", show_alert=True)
        return
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)
    try:
        api = _get_outline_api(server_id, repo, encryption)
        api.delete_key(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return
    logger.info("key deleted server_id=%s key_id=%s", server_id, key_id)
    await call.message.answer("Key deleted.")
    await call.answer()


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery) -> None:
    await call.answer()
