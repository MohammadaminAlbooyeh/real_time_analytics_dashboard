# Encryption at Rest

## Overview

The Real-Time Analytics Dashboard provides **field-level encryption at rest** using the **AES-256-GCM** algorithm via the `cryptography` library (Fernet implementation). Sensitive data is encrypted before being stored in the database and decrypted on read, ensuring data confidentiality even if the database is compromised.

### Encryption Stack

| Component              | Technology                          |
|------------------------|-------------------------------------|
| Algorithm              | AES-256-GCM (via Fernet)            |
| Key Derivation         | PBKDF2HMAC with SHA-256             |
| Key Storage            | PostgreSQL (`encryption_keys` table)|
| Integration            | SQLAlchemy model descriptors        |
| Library                | `cryptography` (Python)             |

---

## Key Management System

### Encryption Key Model

| Field        | Type      | Description                                 |
|--------------|-----------|---------------------------------------------|
| `id`         | UUID      | Auto-generated unique key identifier        |
| `name`       | String    | Human-readable key name                     |
| `key_data`   | Bytes     | Fernet-compatible key (base64-encoded 32-byte key) |
| `algorithm`  | String    | Algorithm identifier (default: "AES-256-GCM")|
| `is_active`  | Boolean   | Whether the key is currently active         |
| `rotated_at` | DateTime  | When the key was rotated (null if never)    |
| `created_at` | DateTime  | When the key was created                    |

### Creating a Key

```python
from backend.services.encryption_service import EncryptionService

service = EncryptionService(session)
key = await service.create_key(
    name="primary-encryption-key",
    passphrase="your-strong-passphrase",
)
print(f"Created key: {key.id} (algorithm: {key.algorithm})")
```

### Listing Keys

```python
keys = await service.list_keys()
for key in keys:
    print(f"{key.name}: active={key.is_active}, algorithm={key.algorithm}")
```

### Loading Keys at Startup

At application startup, all active keys are loaded into an in-memory cache for fast encryption and decryption:

```python
# Called during application initialization
await service.load_keys()
```

---

## Encryption / Decryption Workflow

### Encrypting Data

```python
ciphertext = service.encrypt_value(key_id, "sensitive-data-123")
# Result: "gAAAAAB..." (Fernet-encrypted string)
```

### Decrypting Data

```python
plaintext = service.decrypt_value(key_id, ciphertext)
# Result: "sensitive-data-123"
```

### Key Derivation

Keys are derived from a passphrase using PBKDF2HMAC with SHA-256:

```python
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
```

### Transparent Field Encryption via EncryptedField

The `EncryptedField` descriptor provides transparent encryption/decryption for SQLAlchemy model fields:

```python
from backend.models.encryption_mixin import EncryptedField, EncryptedModelMixin

class User(Base, EncryptedModelMixin):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)

    # Encrypted fields (transparently encrypted/decrypted)
    ssn = EncryptedField("ssn", String(255))
    phone = EncryptedField("phone", String(50))
```

When a value is set, it is automatically encrypted before being stored. When read, it is automatically decrypted.

#### EncryptedJSONField

For storing JSON data, `EncryptedJSONField` serializes the JSON before encryption and deserializes after decryption:

```python
class UserProfile(Base, EncryptedModelMixin):
    __tablename__ = "user_profiles"
    id = Column(UUID, primary_key=True)
    metadata_json = EncryptedJSONField("metadata_json")
```

---

## Key Rotation

### Rotation Process

Key rotation creates a new active encryption key while marking the old key as inactive:

```python
new_key = await service.rotate_key(
    existing_key_id,
    new_passphrase="new-strong-passphrase",
)
```

### What Happens During Rotation

1. The existing key is marked as `is_active = False`
2. The `rotated_at` timestamp is set to the current time
3. A new key is created with the name `{original_name}_rotated`
4. The new key is set as active

### Re-encrypting Data After Rotation

The `EncryptedModelMixin.encrypt_all_fields()` method can be called on model instances to re-encrypt their encrypted fields using the current active key:

```python
# After rotation, re-encrypt existing records
for user in users:
    user.encrypt_all_fields()
    session.add(user)
await session.flush()
```

---

## Configuration

| Environment Variable    | Default   | Description                              |
|-------------------------|-----------|------------------------------------------|
| `ENCRYPTION_ENABLED`    | `false`   | Enable/disable encryption at rest        |
| `ENCRYPTION_KEY`        | `None`    | Default encryption key (optional)        |

### Application Settings

```python
# config/settings.py
encryption_enabled: bool = False
encryption_key: Optional[str] = None
```

### Example `.env` Configuration

```bash
ENCRYPTION_ENABLED=true
ENCRYPTION_KEY=your-encryption-key-here
```

---

## API Endpoints

All encryption endpoints are under **`/api/v1/admin`** and require admin privileges.

### Create Encryption Key

```
POST /api/v1/admin/encryption/keys?name=my-key&passphrase=my-secret
```

**Response:**
```json
{
  "id": "uuid",
  "name": "my-key",
  "algorithm": "AES-256-GCM"
}
```

### List Encryption Keys

```
GET /api/v1/admin/encryption/keys
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "my-key",
    "algorithm": "AES-256-GCM",
    "is_active": true,
    "created_at": "2026-07-21T00:00:00+00:00"
  }
]
```

### Rotate Encryption Key

```
POST /api/v1/admin/encryption/keys/{key_id}/rotate?new_passphrase=new-secret
```

**Response:**
```json
{
  "id": "uuid",
  "name": "my-key_rotated",
  "status": "rotated"
}
```

---

## Security Best Practices

1. **Use Strong Passphrases**: Use long, random passphrases for key derivation
2. **Rotate Keys Regularly**: Implement regular key rotation (e.g., every 90 days)
3. **Backup Keys Securely**: Store key passphrases in a secure vault (e.g., HashiCorp Vault)
4. **Enable Encryption in Production**: Set `ENCRYPTION_ENABLED=true` in production
5. **Monitor Key Usage**: Audit key creation and rotation events

---

## Related Documentation

- [COMPLIANCE.md](./COMPLIANCE.md) - Compliance requirements for encryption
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment guide
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Installation and setup
