import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.alert import AlertRule, AlertEvent, AlertCondition, AlertSeverity, AlertStatus
from backend.utils.logger import get_logger

logger = get_logger("alert_service")


class AlertService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_rule(self, name: str, metric_id: uuid.UUID, condition: AlertCondition,
                          threshold: float, severity: AlertSeverity = AlertSeverity.WARNING,
                          cooldown_minutes: int = 5, description: str | None = None) -> AlertRule:
        rule = AlertRule(
            name=name, metric_id=metric_id, condition=condition,
            threshold=threshold, severity=severity, cooldown_minutes=cooldown_minutes,
            description=description,
        )
        self.session.add(rule)
        await self.session.flush()
        logger.info(f"Created alert rule {rule.id}")
        return rule

    async def get_rule(self, rule_id: uuid.UUID) -> AlertRule | None:
        result = await self.session.execute(select(AlertRule).where(AlertRule.id == rule_id))
        return result.scalar_one_or_none()

    async def list_rules(self, skip: int = 0, limit: int = 100) -> list[AlertRule]:
        result = await self.session.execute(
            select(AlertRule).offset(skip).limit(limit).order_by(AlertRule.created_at.desc())
        )
        return list(result.scalars().all())

    async def evaluate_rule(self, rule: AlertRule, current_value: float) -> AlertEvent | None:
        from backend.utils.logger import get_logger
        triggered = False
        if rule.condition == AlertCondition.GREATER_THAN and current_value > rule.threshold:
            triggered = True
        elif rule.condition == AlertCondition.LESS_THAN and current_value < rule.threshold:
            triggered = True
        elif rule.condition == AlertCondition.EQUAL_TO and current_value == rule.threshold:
            triggered = True

        if not triggered:
            return None

        cooldown_start = datetime.now(timezone.utc) - timedelta(minutes=rule.cooldown_minutes)
        recent = await self.session.execute(
            select(AlertEvent)
            .where(AlertEvent.rule_id == rule.id)
            .where(AlertEvent.status.in_([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]))
            .where(AlertEvent.created_at >= cooldown_start)
            .limit(1)
        )
        if recent.scalar_one_or_none():
            return None

        event = AlertEvent(
            rule_id=rule.id,
            value=current_value,
            status=AlertStatus.ACTIVE,
            message=f"{rule.name}: {current_value} crossed threshold {rule.threshold}",
        )
        self.session.add(event)
        await self.session.flush()
        logger.warning(f"Alert triggered: {rule.name}")
        return event

    async def list_events(self, rule_id: uuid.UUID | None = None, status: AlertStatus | None = None,
                          skip: int = 0, limit: int = 50) -> list[AlertEvent]:
        query = select(AlertEvent)
        if rule_id:
            query = query.where(AlertEvent.rule_id == rule_id)
        if status:
            query = query.where(AlertEvent.status == status)
        query = query.order_by(AlertEvent.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def acknowledge(self, event_id: uuid.UUID, user_id: uuid.UUID) -> AlertEvent | None:
        event = await self.session.execute(select(AlertEvent).where(AlertEvent.id == event_id))
        event = event.scalar_one_or_none()
        if event:
            event.status = AlertStatus.ACKNOWLEDGED
            event.acknowledged_by = user_id
            event.acknowledged_at = datetime.now(timezone.utc)
            await self.session.flush()
        return event

    async def resolve(self, event_id: uuid.UUID) -> AlertEvent | None:
        event = await self.session.execute(select(AlertEvent).where(AlertEvent.id == event_id))
        event = event.scalar_one_or_none()
        if event:
            event.status = AlertStatus.RESOLVED
            event.resolved_at = datetime.now(timezone.utc)
            await self.session.flush()
        return event
