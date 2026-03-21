# Outline Bot

Telegram-бот для управления Outline VPN серверами и ключами доступа (только один администратор).

## Архитектура

```text
bot/
  main.py
  config.py
  logging_config.py
  handlers/
    __init__.py
    common.py
    servers.py
    keys.py
    states.py
  keyboards/
    main_menu.py
    servers.py
    keys.py
  middlewares/
    admin.py
  services/
    database.py
    encryption.py
    outline_api.py
    outline_service.py
    models.py
  utils/
    formatting.py
```

## Outline API (как использовать)

Используется `apiUrl` из `access.txt` или Outline Manager, например:

```json
{"apiUrl":"https://1.2.3.4:1234/UNIQUE_TOKEN"}
```

Важно: отдельная авторизация не нужна, секретом является сам `apiUrl`.

В коде используются endpoint'ы:
- `GET /access-keys/`
- `POST /access-keys`
- `GET /access-keys/{id}`
- `PUT /access-keys/{id}/name` (form-data `name`)
- `DELETE /access-keys/{id}`
- `PUT /server/access-key-data-limit`
- `DELETE /server/access-key-data-limit`

## База данных

SQLite таблица `servers`:
- `id`
- `name`
- `api_url`
- `api_secret_encrypted`
- `created_at`

## Переменные окружения

- `BOT_TOKEN`
- `ADMIN_USER_ID`
- `FERNET_KEY`
- `DATABASE_PATH` (по умолчанию `data/bot.db`)
- `LOG_LEVEL` (по умолчанию `INFO`)

## Локальный запуск (для отладки на ПК)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполните .env
python -m bot.main
```
