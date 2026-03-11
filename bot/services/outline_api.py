"""HTTP client for Outline Access Keys Management API."""

from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import OutlineKey


class OutlineAPIError(RuntimeError):
    """Raised when Outline API call fails."""


class OutlineAPI:
    """Outline API client with retries and typed methods.

    Expected secret URL format from Outline Manager:
    `https://<api_key>@<host>:<port>/<cert-sha256>`
    """

    def __init__(self, api_url: str, timeout: int = 15) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
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
            response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise OutlineAPIError(f"Outline API request failed: {exc}") from exc

        if not response.content:
            return {}

        try:
            return response.json()
        except ValueError as exc:
            raise OutlineAPIError("Outline API returned invalid JSON") from exc

    def list_keys(self) -> list[OutlineKey]:
        payload = self._request("GET", "/access-keys")
        keys_payload = payload.get("accessKeys", [])
        return [OutlineKey.from_api(item) for item in keys_payload]

    def create_key(self, name: str | None = None) -> OutlineKey:
        payload = self._request("POST", "/access-keys")
        key = OutlineKey.from_api(payload)
        if name:
            self.rename_key(key.id, name)
            key.name = name
        return key

    def delete_key(self, key_id: str) -> None:
        self._request("DELETE", f"/access-keys/{key_id}")

    def rename_key(self, key_id: str, name: str) -> None:
        self._request("PUT", f"/access-keys/{key_id}/name", json={"name": name})

    def set_data_limit(self, key_id: str, bytes_limit: int) -> None:
        self._request(
            "PUT",
            f"/access-keys/{key_id}/data-limit",
            json={"limit": {"bytes": bytes_limit}},
        )

    def remove_data_limit(self, key_id: str) -> None:
        self._request("DELETE", f"/access-keys/{key_id}/data-limit")

    def get_key_info(self, key_id: str) -> OutlineKey:
        for key in self.list_keys():
            if key.id == str(key_id):
                return key
        raise OutlineAPIError(f"Access key {key_id} not found")
