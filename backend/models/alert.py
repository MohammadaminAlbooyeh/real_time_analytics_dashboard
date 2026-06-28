import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, Boolean, DateTime, func, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from config.database_config import Base


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCondition(str, enum.Enum):
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUAL_TO = "eq"
    CHANGE_PERCENT = "change_pct"
    ANOMALY = "anomaly"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("metrics.id"), nullable=False
    )
    condition: Mapped[AlertCondition] = mapped_column(
        SAEnum(AlertCondition), nullable=False
    )
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(
        SAEnum(AlertSeverity), default=AlertSeverity.WARNING
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    cooldown_minutes: Mapped[int] = mapped_column(Float, default=5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    metric = relationship("Metric")
    events = relationship("AlertEvent", back_populates="rule", cascade="all, delete-orphan")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alert_rules.id"), nullable=False
    )
    status: Mapped[AlertStatus] = mapped_column(
        SAEnum(AlertStatus), default=AlertStatus.ACTIVE
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    acknowledged_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    rule = relationship("AlertRule", back_populates="events")
    acknowledged_by_user = relationship("User")
