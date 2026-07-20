import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from config.database_config import Base


class WebhookTemplate(Base):
    __tablename__ = "webhook_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    template_body: Mapped[str] = mapped_column(Text, nullable=False)
    template_headers: Mapped[str] = mapped_column(String(2000), nullable=True)
    content_type: Mapped[str] = mapped_column(String(100), default="application/json")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
