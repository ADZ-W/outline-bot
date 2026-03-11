"""Domain-level helper to build Outline API clients from stored servers."""

from __future__ import annotations

from bot.services.database import ServerRepository
from bot.services.encryption import EncryptionService
from bot.services.outline_api import OutlineAPI, OutlineAPIError


class OutlineService:
    """Factory/service for per-server OutlineAPI clients."""

    def __init__(self, repo: ServerRepository, encryption: EncryptionService) -> None:
        self._repo = repo
        self._encryption = encryption

    def get_client(self, server_id: int) -> OutlineAPI:
        """Create OutlineAPI client for the selected server."""
        server = self._repo.get_server(server_id)
        if not server:
            raise OutlineAPIError("Server not found")

        secret_url = self._encryption.decrypt(server.api_secret_encrypted)
        return OutlineAPI(api_url=secret_url)
