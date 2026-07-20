import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.tenant import Tenant
from backend.utils.logger import get_logger

logger = get_logger("tenant_service")


class TenantService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_tenant(
        self, name: str, domain: str | None = None,
        settings_json: str | None = None,
    ) -> Tenant:
        tenant = Tenant(name=name, domain=domain, settings_json=settings_json)
        self.session.add(tenant)
        await self.session.flush()
        logger.info(f"Created tenant {tenant.id}: {name}")
        return tenant

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        result = await self.session.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_domain(self, domain: str) -> Tenant | None:
        result = await self.session.execute(
            select(Tenant).where(Tenant.domain == domain)
        )
        return result.scalar_one_or_none()

    async def list_tenants(self, skip: int = 0, limit: int = 100) -> list[Tenant]:
        result = await self.session.execute(
            select(Tenant).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_tenant(
        self, tenant_id: uuid.UUID, **kwargs
    ) -> Tenant | None:
        tenant = await self.get_by_id(tenant_id)
        if not tenant:
            return None
        for key, value in kwargs.items():
            if hasattr(tenant, key) and value is not None:
                setattr(tenant, key, value)
        await self.session.flush()
        return tenant

    async def delete_tenant(self, tenant_id: uuid.UUID) -> bool:
        tenant = await self.get_by_id(tenant_id)
        if not tenant:
            return False
        await self.session.delete(tenant)
        await self.session.flush()
        return True
