"""Fernet encryption service for sensitive values."""

from cryptography.fernet import Fernet


class EncryptionService:
    """Encrypt/decrypt string payloads via Fernet."""

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode())

    def encrypt(self, value: str) -> str:
        """Encrypt text value to URL-safe token."""
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        """Decrypt URL-safe token back to plain text."""
        return self._fernet.decrypt(value.encode()).decode()
