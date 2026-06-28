import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.models.dashboard import Dashboard, DashboardItem
from backend.utils.logger import get_logger

logger = get_logger("dashboard_service")


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, owner_id: uuid.UUID, description: str | None = None,
                     layout: dict | None = None) -> Dashboard:
        dashboard = Dashboard(
            name=name, owner_id=owner_id, description=description, layout=layout or {},
        )
        self.session.add(dashboard)
        await self.session.flush()
        logger.info(f"Created dashboard {dashboard.id}")
        return dashboard

    async def get_by_id(self, dashboard_id: uuid.UUID) -> Dashboard | None:
        result = await self.session.execute(
            select(Dashboard)
            .where(Dashboard.id == dashboard_id)
            .options(selectinload(Dashboard.items))
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Dashboard]:
        result = await self.session.execute(
            select(Dashboard)
            .where(Dashboard.owner_id == user_id)
            .offset(skip).limit(limit)
            .order_by(Dashboard.updated_at.desc())
        )
        return list(result.scalars().all())

    async def add_item(self, dashboard_id: uuid.UUID, metric_id: uuid.UUID, chart_type: str = "line",
                       title: str | None = None, position_x: int = 0, position_y: int = 0,
                       width: int = 6, height: int = 4, config: dict | None = None) -> DashboardItem:
        item = DashboardItem(
            dashboard_id=dashboard_id, metric_id=metric_id, chart_type=chart_type,
            title=title, position_x=position_x, position_y=position_y,
            width=width, height=height, config=config or {},
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def remove_item(self, item_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(DashboardItem).where(DashboardItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if item:
            await self.session.delete(item)
            await self.session.flush()
            return True
        return False
