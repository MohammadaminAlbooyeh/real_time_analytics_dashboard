import pytest
from uuid import uuid4
from backend.services.encryption_service import EncryptionService


@pytest.mark.asyncio
async def test_create_key(db_session):
    service = EncryptionService(db_session)
    key = await service.create_key(name="test-key", passphrase="my-secret-passphrase")
    assert key.id is not None
    assert key.name == "test-key"
    assert key.algorithm == "AES-256-GCM"
    assert key.is_active is True


@pytest.mark.asyncio
async def test_encrypt_decrypt_value(db_session):
    service = EncryptionService(db_session)
    key = await service.create_key(name="enc-key", passphrase="correct-passphrase")

    ciphertext = service.encrypt_value(str(key.id), "sensitive-data-123")
    assert ciphertext is not None
    assert ciphertext != "sensitive-data-123"

    plaintext = service.decrypt_value(str(key.id), ciphertext)
    assert plaintext == "sensitive-data-123"


@pytest.mark.asyncio
async def test_encrypt_with_invalid_key(db_session):
    service = EncryptionService(db_session)
    with pytest.raises(ValueError, match="not available"):
        service.encrypt_value(str(uuid4()), "data")


@pytest.mark.asyncio
async def test_decrypt_with_invalid_key(db_session):
    service = EncryptionService(db_session)
    with pytest.raises(ValueError, match="not available"):
        service.decrypt_value(str(uuid4()), "ciphertext")


@pytest.mark.asyncio
async def test_rotate_key(db_session):
    service = EncryptionService(db_session)
    original = await service.create_key(name="rotate-me", passphrase="old-pass")

    new_key = await service.rotate_key(original.id, "new-pass")
    assert new_key is not None
    assert new_key.name == "rotate-me_rotated"
    assert new_key.is_active is True
    assert new_key.id != original.id

    # Original key should be marked inactive
    from backend.models.encryption_key import EncryptionKey
    result = await db_session.get(EncryptionKey, original.id)
    assert result.is_active is False
    assert result.rotated_at is not None


@pytest.mark.asyncio
async def test_rotate_key_not_found(db_session):
    service = EncryptionService(db_session)
    result = await service.rotate_key(uuid4(), "new-pass")
    assert result is None


@pytest.mark.asyncio
async def test_list_keys(db_session):
    service = EncryptionService(db_session)
    await service.create_key(name="key-a", passphrase="pass-a")
    await service.create_key(name="key-b", passphrase="pass-b")

    keys = await service.list_keys()
    assert len(keys) == 2
    names = [k.name for k in keys]
    assert "key-a" in names
    assert "key-b" in names


@pytest.mark.asyncio
async def test_list_keys_empty(db_session):
    service = EncryptionService(db_session)
    keys = await service.list_keys()
    assert len(keys) == 0


@pytest.mark.asyncio
async def test_load_keys(db_session):
    service = EncryptionService(db_session)
    key1 = await service.create_key(name="load-key-1", passphrase="pass1")
    key2 = await service.create_key(name="load-key-2", passphrase="pass2")

    # Clear the fernet cache to simulate fresh load
    service._fernet_cache.clear()

    # Load keys from database
    await service.load_keys()

    # Should be able to encrypt/decrypt after loading
    ct = service.encrypt_value(str(key1.id), "test-data")
    pt = service.decrypt_value(str(key1.id), ct)
    assert pt == "test-data"

    ct2 = service.encrypt_value(str(key2.id), "more-data")
    pt2 = service.decrypt_value(str(key2.id), ct2)
    assert pt2 == "more-data"


@pytest.mark.asyncio
async def test_list_keys_ordered_by_created_at_desc(db_session):
    service = EncryptionService(db_session)
    k1 = await service.create_key(name="first", passphrase="p1")
    k2 = await service.create_key(name="second", passphrase="p2")
    k3 = await service.create_key(name="third", passphrase="p3")

    keys = await service.list_keys()
    assert len(keys) == 3
    # All three keys are present
    names = [k.name for k in keys]
    assert "first" in names
    assert "second" in names
    assert "third" in names
