import pytest
from uuid import uuid4
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_get_summary_metric_not_found(client):
    metric_id = str(uuid4())
    response = await client.get(f"/api/v1/analytics/summary/{metric_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_timeseries_invalid_dates(client):
    metric_id = str(uuid4())
    response = await client.get(
        f"/api/v1/analytics/timeseries"
        f"?metric_id={metric_id}&start=invalid&end=2024-01-15"
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_compare_periods_invalid_metric(client):
    payload = {
        "metric_id": str(uuid4()),
        "current_start": "2024-01-08T00:00:00Z",
        "current_end": "2024-01-15T00:00:00Z",
        "previous_start": "2024-01-01T00:00:00Z",
        "previous_end": "2024-01-08T00:00:00Z",
    }

    response = await client.post("/api/v1/analytics/compare", json=payload)
    assert response.status_code == 404
