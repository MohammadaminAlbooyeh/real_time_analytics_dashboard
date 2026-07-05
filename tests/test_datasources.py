import pytest


@pytest.mark.asyncio
async def test_list_datasources_empty(client):
    response = await client.get("/api/v1/datasources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_datasource(client):
    payload = {
        "name": "Test DataSource",
        "type": "http",
        "config": {
            "url": "https://api.example.com",
            "auth_type": "bearer",
        },
        "enabled": True,
    }

    response = await client.post("/api/v1/datasources", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data
