import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from config.database_config import Base


class RetentionPolicy(Base):
    __tablename__ = "retention_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
