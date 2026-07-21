import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_dashboards_empty(auth_client):
    response = await auth_client.get("/api/v1/dashboards")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_dashboard(auth_client):
    payload = {
        "name": "Test Dashboard",
        "description": "A test dashboard",
        "is_public": False,
    }

    response = await auth_client.post("/api/v1/dashboards", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_dashboard_not_found(auth_client):
    dashboard_id = str(uuid4())
    response = await auth_client.get(f"/api/v1/dashboards/{dashboard_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_dashboard_not_found(auth_client):
    dashboard_id = str(uuid4())
    response = await auth_client.delete(f"/api/v1/dashboards/{dashboard_id}")
    assert response.status_code == 404
