"""HTTP-клиент для Outline Access Keys API (apiUrl из access.txt/Manager)."""

from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import OutlineKey


class OutlineAPIError(RuntimeError):
    """Ошибка вызова Outline API."""


class OutlineAPI:
    """Клиент для запросов к Outline Shadowbox API.

    Принимает `apiUrl` формата: `https://host:port/UNIQUE_TOKEN`.
    Авторизация отдельно не требуется, секретом является сам apiUrl.
    """

    def __init__(self, api_url: str, timeout: int = 15, verify_ssl: bool = False) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()

        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.api_url}{path}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise OutlineAPIError(f"Ошибка запроса к Outline API: {exc}") from exc

        if not response.content:
            return {}

        try:
            return response.json()
        except ValueError as exc:
            raise OutlineAPIError("Outline API вернул невалидный JSON") from exc

    def list_keys(self) -> list[OutlineKey]:
        payload = self._request("GET", "/access-keys/")
        keys_payload = payload.get("accessKeys", [])
        return [OutlineKey.from_api(item) for item in keys_payload]

    def create_key(self, name: str | None = None) -> OutlineKey:
        payload = self._request("POST", "/access-keys")
        key = OutlineKey.from_api(payload)
        if name:
            self.rename_key(key.id, name)
            key.name = name
        return key

    def get_key_info(self, key_id: str) -> OutlineKey:
        payload = self._request("GET", f"/access-keys/{key_id}")
        return OutlineKey.from_api(payload)

    def rename_key(self, key_id: str, name: str) -> None:
        self._request("PUT", f"/access-keys/{key_id}/name", data={"name": name})

    def delete_key(self, key_id: str) -> None:
        self._request("DELETE", f"/access-keys/{key_id}")

    def set_data_limit(self, key_id: str, bytes_limit: int) -> None:
        _ = key_id
        self._request("PUT", "/server/access-key-data-limit", json={"limit": {"bytes": bytes_limit}})

    def remove_data_limit(self, key_id: str) -> None:
        _ = key_id
        self._request("DELETE", "/server/access-key-data-limit")
