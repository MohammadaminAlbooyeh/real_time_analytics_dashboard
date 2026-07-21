import pytest


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    response = await client.post(
        "/auth/login",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_and_login(client):
    register_resp = await client.post(
        "/auth/register",
        json={"email": "test2@example.com", "username": "testuser2", "password": "password123"}
    )
    assert register_resp.status_code == 200

    login_resp = await client.post(
        "/auth/login",
        json={"email": "test2@example.com", "password": "password123"}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()
