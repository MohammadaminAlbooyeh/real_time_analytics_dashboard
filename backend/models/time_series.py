import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from config.database_config import Base


class TimeSeriesDataPoint(Base):
    __tablename__ = "time_series_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("metrics.id"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    tags_json: Mapped[str] = mapped_column(String(500), nullable=True)
