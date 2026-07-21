import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_reports_page_uses_analytics_endpoint(auth_client):
    metric_payload = {
        "name": "Report Metric",
        "key": "report_metric",
        "description": "Metric for reports",
        "unit": "count",
        "data_type": "numeric",
        "aggregation_method": "avg",
    }
    create_resp = await auth_client.post("/api/v1/metrics", json=metric_payload)
    assert create_resp.status_code == 201
    metric_id = create_resp.json()["id"]

    summary_resp = await auth_client.get(f"/api/v1/analytics/summary/{metric_id}")
    assert summary_resp.status_code == 200
    data = summary_resp.json()
    assert "avg_last_24h" in data
    assert "avg_last_7d" in data
    assert "datapoints_last_24h" in data


@pytest.mark.asyncio
async def test_reports_export_csv(auth_client):
    metric_payload = {
        "name": "Export Metric",
        "key": "export_metric",
        "description": "Metric for export",
        "unit": "count",
        "data_type": "numeric",
        "aggregation_method": "avg",
    }
    create_resp = await auth_client.post("/api/v1/metrics", json=metric_payload)
    assert create_resp.status_code == 201
    metric_id = create_resp.json()["id"]

    export_resp = await auth_client.get(f"/api/v1/export/csv?metric_id={metric_id}&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z")
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"] == "text/csv; charset=utf-8"
