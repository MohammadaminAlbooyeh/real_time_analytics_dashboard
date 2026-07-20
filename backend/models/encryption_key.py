import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Boolean, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from config.database_config import Base


class EncryptionKey(Base):
    __tablename__ = "encryption_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), default="AES-256-GCM")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rotated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
