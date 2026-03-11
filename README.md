# Outline Bot

Production-oriented Telegram bot for managing multiple Outline VPN servers.

## 1) Project architecture

```text
bot/
  main.py                 # entrypoint (DI wiring, polling)
  config.py               # env config loader
  logging_config.py       # logging setup
  handlers/
    main.py               # telegram handlers + FSM flows
    states.py             # aiogram FSM states
  keyboards/
    inline.py             # inline keyboard builders
  services/
    database.py           # SQLite repository
    encryption.py         # Fernet encryption service
    models.py             # dataclasses
    outline_api.py        # Outline REST API client
```

Architecture principles:
- **Handlers** manage Telegram interaction and FSM only.
- **Services** encapsulate persistence, encryption, and external API logic.
- **Keyboards** isolate UI markup generation.
- **Dependency injection** through aiogram dispatcher context (`repo`, `encryption`, `admin_user_id`).

## 2) Database models

SQLite table `servers`:
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `name TEXT NOT NULL`
- `api_url TEXT NOT NULL`
- `api_secret_encrypted TEXT NOT NULL`
- `created_at TEXT NOT NULL`

`ServerRepository` implements CRUD operations and DB bootstrap at startup.

## 3) Outline API client

`OutlineAPI` service methods:
- `list_keys()`
- `create_key()`
- `delete_key()`
- `rename_key()`
- `set_data_limit()`
- `remove_data_limit()`
- `get_key_info()`

Implementation details:
- Uses `requests.Session`.
- Retries with exponential backoff (`urllib3.Retry`) for transient errors.
- Raises custom `OutlineAPIError` on request/JSON errors.

## 4) Telegram handlers

Implemented in `bot/handlers/main.py` with aiogram 3.x:
- Single-admin access control using `ADMIN_USER_ID`.
- Server management: list/add/rename/delete.
- Server menu and key menu workflows.
- Key operations: create/list/paginated view/open/show/rename/set/remove limit/delete.
- FSM multi-step flows for adding/renaming entities and setting limits.
- Inline keyboard-only UI.

## Environment variables

- `BOT_TOKEN` — Telegram bot token
- `ADMIN_USER_ID` — allowed Telegram user ID
- `FERNET_KEY` — Fernet key (`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
- `DATABASE_PATH` — optional, default `data/bot.db`
- `LOG_LEVEL` — optional, default `INFO`

## Run locally

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
