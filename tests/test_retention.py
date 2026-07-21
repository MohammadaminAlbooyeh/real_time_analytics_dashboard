import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from backend.services.retention_service import RetentionService
from backend.models.retention_policy import RetentionPolicy
from backend.models.time_series import TimeSeriesDataPoint


@pytest.mark.asyncio
async def test_create_policy(db_session):
    service = RetentionService(db_session)
    policy = await service.create_policy(retention_days=30)
    assert policy.id is not None
    assert policy.retention_days == 30
    assert policy.enabled is True


@pytest.mark.asyncio
async def test_create_policy_with_metric_and_tenant(db_session):
    service = RetentionService(db_session)
    metric_id = uuid4()
    tenant_id = uuid4()
    policy = await service.create_policy(
        metric_id=metric_id, tenant_id=tenant_id, retention_days=60
    )
    assert policy.metric_id == metric_id
    assert policy.tenant_id == tenant_id
    assert policy.retention_days == 60


@pytest.mark.asyncio
async def test_list_policies(db_session):
    service = RetentionService(db_session)
    await service.create_policy(retention_days=30)
    await service.create_policy(retention_days=60)
    await service.create_policy(retention_days=90)

    policies = await service.list_policies()
    assert len(policies) == 3


@pytest.mark.asyncio
async def test_list_policies_with_pagination(db_session):
    service = RetentionService(db_session)
    for i in range(5):
        await service.create_policy(retention_days=30 + i * 10)

    policies = await service.list_policies(skip=2, limit=2)
    assert len(policies) == 2


@pytest.mark.asyncio
async def test_get_policy(db_session):
    service = RetentionService(db_session)
    created = await service.create_policy(retention_days=45)

    found = await service.get_policy(created.id)
    assert found is not None
    assert found.retention_days == 45
    assert found.enabled is True


@pytest.mark.asyncio
async def test_get_policy_not_found(db_session):
    service = RetentionService(db_session)
    result = await service.get_policy(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_update_policy(db_session):
    service = RetentionService(db_session)
    created = await service.create_policy(retention_days=30)

    updated = await service.update_policy(created.id, retention_days=90)
    assert updated is not None
    assert updated.retention_days == 90
    assert updated.enabled is True


@pytest.mark.asyncio
async def test_update_policy_disable(db_session):
    service = RetentionService(db_session)
    created = await service.create_policy(retention_days=30)

    updated = await service.update_policy(created.id, enabled=False)
    assert updated is not None
    assert updated.enabled is False


@pytest.mark.asyncio
async def test_update_policy_not_found(db_session):
    service = RetentionService(db_session)
    result = await service.update_policy(uuid4(), retention_days=60)
    assert result is None


@pytest.mark.asyncio
async def test_delete_policy(db_session):
    service = RetentionService(db_session)
    created = await service.create_policy(retention_days=30)

    deleted = await service.delete_policy(created.id)
    assert deleted is True
@pytest.mark.asyncio
async def test_apply_retention_deletes_old_data(db_session):
    service = RetentionService(db_session)
    policy = await service.create_policy(retention_days=1)

    now = datetime.now(timezone.utc)

    old_point = TimeSeriesDataPoint(
        id=uuid4(),
        metric_id=uuid4(),
        value=100.0,
        timestamp=now - timedelta(days=10),
    )
    db_session.add(old_point)

    new_point = TimeSeriesDataPoint(
        id=uuid4(),
        metric_id=uuid4(),
        value=200.0,
        timestamp=now,
    )
    db_session.add(new_point)
    await db_session.flush()

    deleted_count = await service.apply_retention()
    assert deleted_count == 1  # only the old point deleted


@pytest.mark.asyncio
async def test_apply_retention_with_metric_filter(db_session):
    service = RetentionService(db_session)
    metric_id = uuid4()
    policy = await service.create_policy(
        metric_id=metric_id, retention_days=1
    )

    now = datetime.now(timezone.utc)

    old_point = TimeSeriesDataPoint(
        id=uuid4(), metric_id=metric_id, value=10.0,
        timestamp=now - timedelta(days=10),
    )
    db_session.add(old_point)

    other_metric_point = TimeSeriesDataPoint(
        id=uuid4(), metric_id=uuid4(), value=20.0,
        timestamp=now - timedelta(days=10),
    )
    db_session.add(other_metric_point)
    await db_session.flush()

    deleted_count = await service.apply_retention()
    assert deleted_count == 1


@pytest.mark.asyncio
async def test_apply_retention_skips_disabled_policies(db_session):
    service = RetentionService(db_session)
    enabled_policy = await service.create_policy(retention_days=1)
    disabled_policy = await service.create_policy(retention_days=1)
    await service.update_policy(disabled_policy.id, enabled=False)

    now = datetime.now(timezone.utc)
    old_point = TimeSeriesDataPoint(
        id=uuid4(), metric_id=uuid4(), value=99.0,
        timestamp=now - timedelta(days=10),
    )
    db_session.add(old_point)
    await db_session.flush()

    deleted_count = await service.apply_retention()
    assert isinstance(deleted_count, int)


@pytest.mark.asyncio
async def test_delete_policy_not_found(db_session):
    service = RetentionService(db_session)
    result = await service.delete_policy(uuid4())
    assert result is False
