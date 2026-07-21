import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_alert_rules_empty(auth_client):
    response = await auth_client.get("/api/v1/alerts/rules")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_alert_rule_invalid_metric(auth_client):
    payload = {
        "name": "Test Alert",
        "metric_id": str(uuid4()),
        "condition": "gt",
        "threshold": 100,
        "severity": "warning",
        "enabled": True,
    }

    response = await auth_client.post("/api/v1/alerts/rules", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_alert_events_empty(auth_client):
    response = await auth_client.get("/api/v1/alerts/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
