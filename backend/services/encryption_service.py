import uuid
import json
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.encryption_key import EncryptionKey
from backend.utils.logger import get_logger

logger = get_logger("encryption_service")


class EncryptionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._fernet_cache: dict[str, Fernet] = {}

    @staticmethod
    def _derive_key(password: str, salt: bytes = b"analytics_salt") -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    async def create_key(self, name: str, passphrase: str) -> EncryptionKey:
        key = self._derive_key(passphrase)
        encrypted_key = EncryptionKey(
            name=name,
            key_data=key,
            algorithm="AES-256-GCM",
        )
        self.session.add(encrypted_key)
        await self.session.flush()
        logger.info(f"Created encryption key {encrypted_key.id}")
        self._fernet_cache[str(encrypted_key.id)] = Fernet(key)
        return encrypted_key

    def _get_fernet(self, key_id: str) -> Fernet | None:
        if key_id in self._fernet_cache:
            return self._fernet_cache[key_id]
        return None

    def encrypt_value(self, key_id: str, plaintext: str) -> str:
        fernet = self._get_fernet(key_id)
        if not fernet:
            raise ValueError(f"Encryption key {key_id} not available")
        return fernet.encrypt(plaintext.encode()).decode()

    def decrypt_value(self, key_id: str, ciphertext: str) -> str:
        fernet = self._get_fernet(key_id)
        if not fernet:
            raise ValueError(f"Encryption key {key_id} not available")
        return fernet.decrypt(ciphertext.encode()).decode()

    async def load_keys(self):
        result = await self.session.execute(
            select(EncryptionKey).where(EncryptionKey.is_active == True)
        )
        keys = list(result.scalars().all())
        for key in keys:
            try:
                self._fernet_cache[str(key.id)] = Fernet(key.key_data)
            except Exception as e:
                logger.error(f"Failed to load key {key.id}: {e}")
        logger.info(f"Loaded {len(keys)} encryption keys")

    async def rotate_key(self, key_id: uuid.UUID, new_passphrase: str) -> EncryptionKey | None:
        key = await self.session.execute(
            select(EncryptionKey).where(EncryptionKey.id == key_id)
        )
        key = key.scalar_one_or_none()
        if not key:
            return None
        key.is_active = False
        key.rotated_at = datetime.now()
        new_key = await self.create_key(f"{key.name}_rotated", new_passphrase)
        await self.session.flush()
        return new_key

    async def list_keys(self) -> list[EncryptionKey]:
        result = await self.session.execute(
            select(EncryptionKey).order_by(EncryptionKey.created_at.desc())
        )
        return list(result.scalars().all())
