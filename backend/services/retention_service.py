import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.retention_policy import RetentionPolicy
from backend.models.time_series import TimeSeriesDataPoint
from backend.utils.logger import get_logger

logger = get_logger("retention_service")


class RetentionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_policy(
        self, metric_id: uuid.UUID | None = None,
        tenant_id: uuid.UUID | None = None,
        retention_days: int = 90,
    ) -> RetentionPolicy:
        policy = RetentionPolicy(
            metric_id=metric_id,
            tenant_id=tenant_id,
            retention_days=retention_days,
        )
        self.session.add(policy)
        await self.session.flush()
        logger.info(f"Created retention policy {policy.id}: {retention_days} days")
        return policy

    async def list_policies(self, skip: int = 0, limit: int = 100) -> list[RetentionPolicy]:
        result = await self.session.execute(
            select(RetentionPolicy).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_policy(self, policy_id: uuid.UUID) -> RetentionPolicy | None:
        result = await self.session.execute(
            select(RetentionPolicy).where(RetentionPolicy.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def update_policy(
        self, policy_id: uuid.UUID, retention_days: int | None = None,
        enabled: bool | None = None,
    ) -> RetentionPolicy | None:
        policy = await self.get_policy(policy_id)
        if not policy:
            return None
        if retention_days is not None:
            policy.retention_days = retention_days
        if enabled is not None:
            policy.enabled = enabled
        await self.session.flush()
        return policy

    async def delete_policy(self, policy_id: uuid.UUID) -> bool:
        policy = await self.get_policy(policy_id)
        if not policy:
            return False
        await self.session.delete(policy)
        await self.session.flush()
        return True

    async def apply_retention(self) -> int:
        """Apply all enabled retention policies and return count of deleted data points."""
        result = await self.session.execute(
            select(RetentionPolicy).where(RetentionPolicy.enabled == True)
        )
        policies = list(result.scalars().all())
        total_deleted = 0
        now = datetime.now(timezone.utc)
        for policy in policies:
            cutoff = now - timedelta(days=policy.retention_days)
            query = delete(TimeSeriesDataPoint).where(
                TimeSeriesDataPoint.timestamp < cutoff
            )
            if policy.metric_id:
                query = query.where(TimeSeriesDataPoint.metric_id == policy.metric_id)
            result = await self.session.execute(query)
            total_deleted += result.rowcount
            logger.info(
                f"Retention policy {policy.id}: deleted {result.rowcount} records "
                f"older than {cutoff.isoformat()}"
            )
        await self.session.flush()
        return total_deleted
