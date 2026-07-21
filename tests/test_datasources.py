import pytest


@pytest.mark.asyncio
async def test_list_datasources_empty(auth_client):
    response = await auth_client.get("/api/v1/datasources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_datasource(auth_client):
    payload = {
        "name": "Test DataSource",
        "type": "api",
        "config_json": '{"url": "https://api.example.com"}',
    }

    response = await auth_client.post("/api/v1/datasources", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data
