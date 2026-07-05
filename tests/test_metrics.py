import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_metrics_empty(client):
    response = await client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_metric(client):
    payload = {
        "name": "Test Metric",
        "key": "test_metric",
        "description": "A test metric",
        "unit": "ms",
        "data_type": "numeric",
        "aggregation_method": "avg",
    }

    response = await client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["key"] == payload["key"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_metric_duplicate_key(client):
    payload = {
        "name": "Test Metric",
        "key": "test_metric",
        "description": "A test metric",
        "unit": "ms",
        "data_type": "numeric",
        "aggregation_method": "avg",
    }

    await client.post("/api/v1/metrics", json=payload)
    response = await client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_metric_not_found(client):
    metric_id = str(uuid4())
    response = await client.get(f"/api/v1/metrics/{metric_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_record_metric_data_invalid_id(client):
    metric_id = str(uuid4())
    payload = {
        "value": 100.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }

    response = await client.post(
        f"/api/v1/metrics/{metric_id}/data",
        json=payload
    )
    assert response.status_code == 404
