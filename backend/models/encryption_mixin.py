"""
Encryption Mixin for SQLAlchemy Models

Provides transparent field-level encryption/decryption for sensitive data
in database models using the existing EncryptionService.

Usage:
    from backend.models.encryption_mixin import EncryptedField, EncryptedModelMixin

    class User(Base, EncryptedModelMixin):
        __tablename__ = "users"
        id = Column(UUID, primary_key=True)
        email = Column(String, unique=True)
        # Encrypted fields
        ssn = EncryptedField("ssn", String(255))
        phone = EncryptedField("phone", String(50))
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger("encryption_mixin")

# Global reference to the encryption service (set at app startup)
_encryption_service: Optional[Any] = None
_default_key_id: Optional[str] = None


def set_encryption_service(service: Any, key_id: Optional[str] = None) -> None:
    """Set the global encryption service instance.

    Called once at application startup (e.g., in main.py lifespan).
    """
    global _encryption_service, _default_key_id
    _encryption_service = service
    _default_key_id = key_id
    logger.info(f"Encryption service initialized (key_id={key_id})")


def get_encryption_service() -> Any:
    """Return the global encryption service instance."""
    if _encryption_service is None:
        raise RuntimeError(
            "EncryptionService not initialized. Call set_encryption_service() "
            "during application startup."
        )
    return _encryption_service


class EncryptedField:
    """Descriptor that transparently encrypts/decrypts a model field value.

    Stores encrypted data in the database and decrypts on read.
    Uses Fernet (AES-256-GCM) via the EncryptionService.

    Example:
        class User(Base):
            __tablename__ = "users"
            id = Column(UUID, primary_key=True)
            email = Column(String, unique=True)
            ssn = EncryptedField("ssn", String(255))
    """

    def __init__(
        self,
        column_name: str,
        column_type: Any = None,
        key_id: Optional[str] = None,
        nullable: bool = True,
    ):
        self._column_name = column_name
        self._column_type = column_type
        self._key_id = key_id
        self._nullable = nullable
        self._attribute_name: Optional[str] = None

    def __set_name__(self, owner: Any, name: str) -> None:
        self._attribute_name = name

    def __get__(self, instance: Optional[Any], owner: Any) -> Any:
        if instance is None:
            return self

        ciphertext = instance.__dict__.get(self._column_name)
        if ciphertext is None:
            return None

        try:
            service = get_encryption_service()
            key_id = self._key_id or _default_key_id
            if key_id is None:
                raise ValueError(
                    "No encryption key_id provided. Pass key_id to EncryptedField "
                    "or call set_encryption_service() with a default key."
                )
            return service.decrypt_value(key_id, ciphertext)
        except Exception as exc:
            logger.error(
                "Failed to decrypt field '%s' on %s: %s",
                self._column_name,
                owner.__name__,
                exc,
            )
            raise

    def __set__(self, instance: Any, value: Any) -> None:
        if value is None and self._nullable:
            instance.__dict__[self._column_name] = None
            return

        try:
            service = get_encryption_service()
            key_id = self._key_id or _default_key_id
            if key_id is None:
                raise ValueError(
                    "No encryption key_id provided. Pass key_id to EncryptedField "
                    "or call set_encryption_service() with a default key."
                )
            instance.__dict__[self._column_name] = service.encrypt_value(
                key_id, str(value)
            )
        except Exception as exc:
            logger.error(
                "Failed to encrypt field '%s' on %s: %s",
                self._column_name,
                type(instance).__name__,
                exc,
            )
            raise


class EncryptedModelMixin:
    """Mixin that integrates EncryptedField support with SQLAlchemy models.

    Automatically maps encrypted fields as regular SQLAlchemy columns
    so that Alembic migrations work correctly.

    Include this mixin before Base in your model declaration.
    """

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

    def encrypt_all_fields(self) -> None:
        """Re-encrypt all encrypted fields on this instance.

        Useful after key rotation: loads plaintext and re-saves with a new key.
        """
        for attr_name in dir(self):
            descriptor = getattr(type(self), attr_name, None)
            if isinstance(descriptor, EncryptedField):
                plaintext = getattr(self, attr_name)
                if plaintext is not None:
                    setattr(self, attr_name, plaintext)


class EncryptedJSONField(EncryptedField):
    """EncryptedField variant that transparently serializes/deserializes JSON.

    Stores dict or list values as encrypted JSON strings in the database.

    Example:
        class UserProfile(Base, EncryptedModelMixin):
            __tablename__ = "user_profiles"
            id = Column(UUID, primary_key=True)
            metadata_json = EncryptedJSONField("metadata_json")
    """

    def __get__(self, instance: Optional[Any], owner: Any) -> Any:
        if instance is None:
            return self
        raw = super().__get__(instance, owner)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error(
                "Failed to decode encrypted JSON field '%s': %s",
                self._column_name, exc,
            )
            return None

    def __set__(self, instance: Any, value: Any) -> None:
        if value is None and self._nullable:
            super().__set__(instance, None)
            return
        super().__set__(instance, json.dumps(value, default=str))
