import pytest


METRICS_QUERY = """
query {
    metrics {
        id
        name
        key
        data_type
        is_active
    }
}
"""

METRIC_QUERY = """
query($id: String!) {
    metric(metric_id: $id) {
        id
        name
        key
    }
}
"""

TIMESERIES_QUERY = """
query($metricId: String!, $start: String!, $end: String!) {
    timeseries(metric_id: $metricId, start: $start, end: $end) {
        id
        metric_id
        value
        timestamp
    }
}
"""

ANOMALIES_QUERY = """
query($metricId: String!) {
    anomalies(metric_id: $metricId) {
        timestamp
        value
        anomaly_score
        severity
    }
}
"""

FORECASTS_QUERY = """
query($metricId: String!) {
    forecasts(metric_id: $metricId, forecast_hours: 5) {
        timestamp
        predicted_value
        confidence_lower
        confidence_upper
    }
}
"""

ANALYTICS_SUMMARY_QUERY = """
query($metricId: String!) {
    analytics_summary(metric_id: $metricId) {
        avg_last_24h
        avg_last_7d
        datapoints_last_24h
    }
}
"""

ALERT_RULES_QUERY = """
query {
    alert_rules {
        id
        name
        metric_id
        condition
        threshold
        severity
        enabled
    }
}
"""


def _post_graphql(client, query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    return client.post("/graphql", json=payload)


@pytest.mark.asyncio
async def test_graphql_metrics_query(client):
    response = await _post_graphql(client, METRICS_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "metrics" in data["data"]
    assert isinstance(data["data"]["metrics"], list)


@pytest.mark.asyncio
async def test_graphql_metric_query(client):
    variables = {"id": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(client, METRIC_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    # metric may be null if not found, but query should not error
    assert data["data"]["metric"] is None or isinstance(data["data"]["metric"], dict)


@pytest.mark.asyncio
async def test_graphql_timeseries_query(client):
    variables = {
        "metricId": "00000000-0000-0000-0000-000000000001",
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-02T00:00:00Z",
    }
    response = await _post_graphql(client, TIMESERIES_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"]["timeseries"], list)


@pytest.mark.asyncio
async def test_graphql_anomalies_query(client):
    variables = {"metricId": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(client, ANOMALIES_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"]["anomalies"], list)


@pytest.mark.asyncio
async def test_graphql_forecasts_query(client):
    variables = {"metricId": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(client, FORECASTS_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"]["forecasts"], list)


@pytest.mark.asyncio
async def test_graphql_analytics_summary_query(client):
    variables = {"metricId": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(client, ANALYTICS_SUMMARY_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    summary = data["data"]["analytics_summary"]
    # Should return a valid summary (possibly with nulls)
    assert summary is not None
    assert "avg_last_24h" in summary
    assert "avg_last_7d" in summary
    assert "datapoints_last_24h" in summary


@pytest.mark.asyncio
async def test_graphql_alert_rules_query(client):
    response = await _post_graphql(client, ALERT_RULES_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"]["alert_rules"], list)


@pytest.mark.asyncio
async def test_graphql_invalid_query(client):
    response = await _post_graphql(client, "{ invalidField }")
    assert response.status_code == 400
    data = response.json()
    assert "errors" in data


@pytest.mark.asyncio
async def test_graphql_metrics_after_creating_one(client):
    from uuid import uuid4
    from backend.main import app
    from backend.api.dependencies import get_admin_user
    from unittest.mock import MagicMock
    from backend.models.user import User

    # Create a metric via the API first
    payload = {
        "name": "GraphQL Metric",
        "key": "graphql_test_metric",
        "description": "Created for GraphQL test",
        "unit": "count",
        "data_type": "numeric",
        "aggregation_method": "sum",
    }
    response = await client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 201

    # Query via GraphQL
    resp = await _post_graphql(client, METRICS_QUERY)
    assert resp.status_code == 200
    data = resp.json()
    metrics = data["data"]["metrics"]
    names = [m["name"] for m in metrics]
    assert "GraphQL Metric" in names
