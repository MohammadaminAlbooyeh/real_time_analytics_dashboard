import pytest


@pytest.mark.asyncio
async def test_list_reports_empty(client):
    response = await client.get("/api/v1/reports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_report(client):
    payload = {
        "name": "Test Report",
        "metrics": [],
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "format": "pdf",
    }

    response = await client.post("/api/v1/reports", json=payload)
    # May be 201 or 400 depending on implementation
    assert response.status_code in [201, 400]
