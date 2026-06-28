import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.data_source import DataSource, DataSourceType, DataSourceStatus
from backend.utils.logger import get_logger

logger = get_logger("data_source_service")


class DataSourceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, source_type: DataSourceType, config_json: str | None = None) -> DataSource:
        ds = DataSource(name=name, type=source_type, config_json=config_json)
        self.session.add(ds)
        await self.session.flush()
        logger.info(f"Created data source {ds.id}")
        return ds

    async def get_by_id(self, ds_id: uuid.UUID) -> DataSource | None:
        result = await self.session.execute(select(DataSource).where(DataSource.id == ds_id))
        return result.scalar_one_or_none()

    async def list_sources(self, skip: int = 0, limit: int = 100) -> list[DataSource]:
        result = await self.session.execute(
            select(DataSource).offset(skip).limit(limit).order_by(DataSource.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(self, ds_id: uuid.UUID, status: DataSourceStatus,
                            error_message: str | None = None) -> DataSource | None:
        ds = await self.get_by_id(ds_id)
        if ds:
            ds.status = status
            if status == DataSourceStatus.ACTIVE:
                ds.last_collected_at = datetime.now(timezone.utc)
            if error_message:
                ds.error_message = error_message
            await self.session.flush()
        return ds

    async def delete(self, ds_id: uuid.UUID) -> bool:
        ds = await self.get_by_id(ds_id)
        if ds:
            await self.session.delete(ds)
            await self.session.flush()
            return True
        return False
