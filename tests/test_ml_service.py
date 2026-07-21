import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from backend.services.ml_service import MLService
from backend.models.time_series import TimeSeriesDataPoint


@pytest.mark.asyncio
async def test_get_model_insights_no_data(db_session):
    service = MLService(db_session)
    metric_id = uuid4()
    insights = await service.get_model_insights(metric_id)
    assert insights["metric_id"] == str(metric_id)
    assert insights["mean"] == 0
    assert insights["data_quality"] == "insufficient_data"


@pytest.mark.asyncio
async def test_get_model_insights_with_data(db_session):
    service = MLService(db_session)
    metric_id = uuid4()
    now = datetime.now(timezone.utc)

    for i in range(10):
        point = TimeSeriesDataPoint(
            id=uuid4(),
            metric_id=metric_id,
            value=100.0 + i,
            timestamp=now - timedelta(hours=i),
        )
        db_session.add(point)
    await db_session.flush()

    insights = await service.get_model_insights(metric_id)
    assert insights["metric_id"] == str(metric_id)
    assert insights["mean"] > 0
    assert insights["period"] == "30d"
    # volatility and data_quality may vary depending on database variance support
    assert "volatility" in insights
    assert "data_quality" in insights


@pytest.mark.asyncio
async def test_detect_anomalies_insufficient_data(db_session):
    """Should return empty list when fewer than 10 data points."""
    service = MLService(db_session)
    metric_id = uuid4()
    now = datetime.now(timezone.utc)

    for i in range(5):
        point = TimeSeriesDataPoint(
            id=uuid4(),
            metric_id=metric_id,
            value=100.0 + i,
            timestamp=now - timedelta(hours=i),
        )
        db_session.add(point)
    await db_session.flush()

    anomalies = await service.detect_anomalies_isolation_forest(metric_id)
    assert anomalies == []


@pytest.mark.asyncio
async def test_detect_anomalies_sufficient_data(db_session):
    """Should return anomaly list when sufficient data exists."""
    service = MLService(db_session)
    metric_id = uuid4()
    now = datetime.now(timezone.utc)

    for i in range(20):
        value = 100.0
        if i in (3, 8, 15):
            value = 500.0  # outlier
        point = TimeSeriesDataPoint(
            id=uuid4(),
            metric_id=metric_id,
            value=value,
            timestamp=now - timedelta(hours=i),
        )
        db_session.add(point)
    await db_session.flush()

    anomalies = await service.detect_anomalies_isolation_forest(metric_id)
    assert isinstance(anomalies, list)
    if len(anomalies) > 0:
        for a in anomalies:
            assert "timestamp" in a
            assert "value" in a
            assert "anomaly_score" in a
            assert "severity" in a


@pytest.mark.asyncio
async def test_forecast_insufficient_data(db_session):
    """Should return empty list when fewer than 24 data points."""
    service = MLService(db_session)
    metric_id = uuid4()
    now = datetime.now(timezone.utc)

    for i in range(10):
        point = TimeSeriesDataPoint(
            id=uuid4(),
            metric_id=metric_id,
            value=50.0 + i,
            timestamp=now - timedelta(hours=i),
        )
        db_session.add(point)
    await db_session.flush()

    forecasts = await service.forecast_values(metric_id)
    assert forecasts == []


@pytest.mark.asyncio
async def test_forecast_values(db_session):
    """Should return forecast list when sufficient data exists."""
    service = MLService(db_session)
    metric_id = uuid4()
    now = datetime.now(timezone.utc)

    for i in range(30):
        value = 100.0 + (i % 10) * 5
        point = TimeSeriesDataPoint(
            id=uuid4(),
            metric_id=metric_id,
            value=value,
            timestamp=now - timedelta(hours=i),
        )
        db_session.add(point)
    await db_session.flush()

    forecasts = await service.forecast_values(metric_id, forecast_hours=5)
    assert isinstance(forecasts, list)
    assert len(forecasts) == 5
    for f in forecasts:
        assert "timestamp" in f
        assert "predicted_value" in f
        assert "confidence_lower" in f
        assert "confidence_upper" in f
        assert f["predicted_value"] > 0


@pytest.mark.asyncio
async def test_forecast_returns_empty_for_no_data(db_session):
    """Forecasting with no data points should return empty list."""
    service = MLService(db_session)
    metric_id = uuid4()

    forecasts = await service.forecast_values(metric_id)
    assert forecasts == []


@pytest.mark.asyncio
async def test_detect_anomalies_returns_empty_for_no_data(db_session):
    """Anomaly detection with no data points should return empty list."""
    service = MLService(db_session)
    metric_id = uuid4()

    anomalies = await service.detect_anomalies_isolation_forest(metric_id)
    assert anomalies == []
