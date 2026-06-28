import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database_config import Base


class Dashboard(Base):
    __tablename__ = "dashboards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    layout: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_interval: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", backref="dashboards")
    items = relationship("DashboardItem", back_populates="dashboard", cascade="all, delete-orphan")


class DashboardItem(Base):
    __tablename__ = "dashboard_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=False
    )
    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("metrics.id"), nullable=False
    )
    chart_type: Mapped[str] = mapped_column(String(50), nullable=False, default="line")
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    position_x: Mapped[int] = mapped_column(Integer, default=0)
    position_y: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, default=6)
    height: Mapped[int] = mapped_column(Integer, default=4)
    config: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    dashboard = relationship("Dashboard", back_populates="items")
    metric = relationship("Metric")
