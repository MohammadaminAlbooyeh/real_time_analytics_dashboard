import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_user_password_hashing():
    from backend.models.user import User

    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password="hashed-secret",
        is_active=True,
        is_admin=False,
    )

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password == "hashed-secret"
    assert user.is_active is True
    assert user.is_admin is False


@pytest.mark.asyncio
async def test_metric_creation():
    from backend.models.metric import Metric

    metric = Metric(
        id=uuid4(),
        name="Test Metric",
        key="test_metric",
        unit="ms",
        data_type="numeric",
        aggregation_method="avg",
    )

    assert metric.name == "Test Metric"
    assert metric.key == "test_metric"
    assert metric.unit == "ms"
