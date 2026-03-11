"""Access key management handlers."""

from __future__ import annotations

import logging
from math import ceil

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import key_menu_keyboard, keys_keyboard
from bot.services.outline_api import OutlineAPIError
from bot.services.outline_service import OutlineService
from bot.utils.formatting import format_bytes

from .states import KeyStates

logger = logging.getLogger(__name__)
router = Router(name="keys")


@router.callback_query(F.data.startswith("keys:create:"))
async def create_key(call: CallbackQuery, outline: OutlineService) -> None:
    server_id = int(call.data.split(":")[2])
    try:
        key = outline.get_client(server_id).create_key()
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    logger.info("key created server_id=%s key_id=%s", server_id, key.id)
    await call.message.answer(f"Created key {key.id}")
    await call.answer()


@router.callback_query(F.data.startswith("keys:list:"))
async def list_keys(call: CallbackQuery, outline: OutlineService) -> None:
    _, _, server_id_s, page_s = call.data.split(":")
    server_id, page = int(server_id_s), int(page_s)

    try:
        keys = outline.get_client(server_id).list_keys()
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    per_page = 10
    total_pages = max(1, ceil(len(keys) / per_page))
    page = min(max(page, 1), total_pages)
    start = (page - 1) * per_page
    paged_keys = keys[start : start + per_page]

    await call.message.edit_text(
        f"Access keys ({len(keys)} total)",
        reply_markup=keys_keyboard(server_id=server_id, keys=paged_keys, page=page, total_pages=total_pages),
    )
    await call.answer()


@router.callback_query(F.data.startswith("keys:open:"))
async def open_key(call: CallbackQuery, outline: OutlineService) -> None:
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)

    try:
        key = outline.get_client(server_id).get_key_info(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    text = (
        f"Name: {key.name}\n"
        f"ID: {key.id}\n"
        f"Data used: {format_bytes(key.used_bytes)}\n"
        f"Data limit: {format_bytes(key.data_limit_bytes)}"
    )
    await call.message.edit_text(text, reply_markup=key_menu_keyboard(server_id, key_id))
    await call.answer()


@router.callback_query(F.data.startswith("keys:show:"))
async def show_key(call: CallbackQuery, outline: OutlineService) -> None:
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)

    try:
        key = outline.get_client(server_id).get_key_info(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    await call.message.answer(f"Access URL:\n{key.access_url}")
    await call.answer()


@router.callback_query(F.data.startswith("keys:rename:"))
async def rename_key_start(call: CallbackQuery, state: FSMContext) -> None:
    _, _, server_id_s, key_id = call.data.split(":")
    await state.set_state(KeyStates.renaming)
    await state.update_data(server_id=int(server_id_s), key_id=key_id)
    await call.message.answer("Send new key name:")
    await call.answer()


@router.message(KeyStates.renaming)
async def rename_key_finish(message: Message, state: FSMContext, outline: OutlineService) -> None:
    data = await state.get_data()
    server_id = int(data["server_id"])
    key_id = str(data["key_id"])

    try:
        outline.get_client(server_id).rename_key(key_id, message.text.strip())
    except OutlineAPIError as exc:
        await message.answer(str(exc))
        return

    await state.clear()
    await message.answer("Key renamed.")


@router.callback_query(F.data.startswith("keys:set_limit:"))
async def set_limit_start(call: CallbackQuery, state: FSMContext) -> None:
    _, _, server_id_s, key_id = call.data.split(":")
    await state.set_state(KeyStates.setting_limit)
    await state.update_data(server_id=int(server_id_s), key_id=key_id)
    await call.message.answer("Send data limit in GB (positive integer):")
    await call.answer()


@router.message(KeyStates.setting_limit)
async def set_limit_finish(message: Message, state: FSMContext, outline: OutlineService) -> None:
    try:
        limit_gb = int(message.text.strip())
        if limit_gb <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Please send a positive integer value (GB).")
        return

    data = await state.get_data()
    server_id = int(data["server_id"])
    key_id = str(data["key_id"])
    bytes_limit = limit_gb * 1024 * 1024 * 1024

    try:
        outline.get_client(server_id).set_data_limit(key_id, bytes_limit)
    except OutlineAPIError as exc:
        await message.answer(str(exc))
        return

    logger.info("limit changed server_id=%s key_id=%s bytes=%s", server_id, key_id, bytes_limit)
    await state.clear()
    await message.answer("Data limit updated.")


@router.callback_query(F.data.startswith("keys:remove_limit:"))
async def remove_limit(call: CallbackQuery, outline: OutlineService) -> None:
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)

    try:
        outline.get_client(server_id).remove_data_limit(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    logger.info("limit changed server_id=%s key_id=%s removed=true", server_id, key_id)
    await call.message.answer("Data limit removed.")
    await call.answer()


@router.callback_query(F.data.startswith("keys:delete:"))
async def delete_key(call: CallbackQuery, outline: OutlineService) -> None:
    _, _, server_id_s, key_id = call.data.split(":")
    server_id = int(server_id_s)

    try:
        outline.get_client(server_id).delete_key(key_id)
    except OutlineAPIError as exc:
        await call.answer(str(exc), show_alert=True)
        return

    logger.info("key deleted server_id=%s key_id=%s", server_id, key_id)
    await call.message.answer("Key deleted.")
    await call.answer()
