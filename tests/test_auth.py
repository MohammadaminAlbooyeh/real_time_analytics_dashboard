import pytest


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 422
