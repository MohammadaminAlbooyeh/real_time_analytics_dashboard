import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_user_password_hashing():
    from backend.models.user import User

    user = User(email="test@example.com", name="Test")
    user.set_password("mypassword")

    assert user.hashed_password != "mypassword"
    assert user.check_password("mypassword")
    assert not user.check_password("wrongpassword")


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
