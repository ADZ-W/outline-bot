# Outline Bot

Telegram-бот для управления несколькими Outline VPN серверами (single-admin).

## 1) Архитектура проекта

```text
bot/
  main.py                    # entrypoint, DI, middleware, polling
  config.py                  # env-конфиг
  logging_config.py          # logging
  handlers/
    __init__.py              # сборка root router
    common.py                # /start, main, noop
    servers.py               # сценарии управления серверами
    keys.py                  # сценарии управления ключами
    states.py                # FSM состояния
  keyboards/
    main_menu.py             # главное меню
    servers.py               # меню серверов
    keys.py                  # меню ключей
  middlewares/
    admin.py                 # single-admin guard
  services/
    database.py              # SQLite repository
    encryption.py            # Fernet encryption service
    outline_api.py           # Outline Access Keys Management API client
    outline_service.py       # получение клиента по server_id
    models.py                # dataclasses
  utils/
    formatting.py            # форматирование байт
```

## 2) Database model

Таблица `servers`:
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `name TEXT NOT NULL`
- `api_url TEXT NOT NULL`
- `api_secret_encrypted TEXT NOT NULL`
- `created_at TEXT NOT NULL`

## 3) Outline API client (официальный Access Keys Management API)

Источник: официальная документация Outline Shadowbox Access Keys API:
- `/access-keys` (GET/POST)
- `/access-keys/{id}` (DELETE)
- `/access-keys/{id}/name` (PUT)
- `/access-keys/{id}/data-limit` (PUT/DELETE)

Реализованные методы:
- `list_keys()`
- `create_key()`
- `delete_key()`
- `rename_key()`
- `set_data_limit()`
- `remove_data_limit()`
- `get_key_info()`

## 4) Telegram handlers

- Полный inline UI.
- FSM для multi-step действий.
- Single-admin доступ через middleware и `ADMIN_USER_ID`.
- Управление серверами: list/add/rename/delete.
- Управление ключами: create/list (pagination 10)/open/show/rename/set-limit/remove-limit/delete.

## Environment variables

- `BOT_TOKEN`
- `ADMIN_USER_ID`
- `FERNET_KEY`
- `DATABASE_PATH` (default: `data/bot.db`)
- `LOG_LEVEL` (default: `INFO`)

## Run local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

## Docker

```bash
docker compose up --build -d
```
