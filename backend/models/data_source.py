import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum
from config.database_config import Base


class DataSourceType(str, enum.Enum):
    API = "api"
    DATABASE = "database"
    FILE = "file"
    WEB_SCRAPER = "web_scraper"


class DataSourceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[DataSourceType] = mapped_column(SAEnum(DataSourceType), nullable=False)
    config_json: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[DataSourceStatus] = mapped_column(
        SAEnum(DataSourceStatus), default=DataSourceStatus.ACTIVE
    )
    last_collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
