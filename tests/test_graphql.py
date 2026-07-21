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
async def test_graphql_metrics_query(auth_client):
    response = await _post_graphql(auth_client, METRICS_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"].get("metrics"), list)


@pytest.mark.asyncio
async def test_graphql_metric_query(auth_client):
    variables = {"id": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(auth_client, METRIC_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    # metric may be null if not found, but query should not error
    assert data["data"].get("metric") is None or isinstance(data["data"].get("metric"), dict)


@pytest.mark.asyncio
async def test_graphql_timeseries_query(auth_client):
    variables = {
        "metricId": "00000000-0000-0000-0000-000000000001",
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-02T00:00:00Z",
    }
    response = await _post_graphql(auth_client, TIMESERIES_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"].get("timeseries"), list)


@pytest.mark.asyncio
async def test_graphql_anomalies_query(auth_client):
    variables = {"metricId": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(auth_client, ANOMALIES_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"].get("anomalies"), list)


@pytest.mark.asyncio
async def test_graphql_forecasts_query(auth_client):
    variables = {"metricId": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(auth_client, FORECASTS_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"].get("forecasts"), list)


@pytest.mark.asyncio
async def test_graphql_analytics_summary_query(auth_client):
    variables = {"metricId": "00000000-0000-0000-0000-000000000001"}
    response = await _post_graphql(auth_client, ANALYTICS_SUMMARY_QUERY, variables)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    summary = data["data"].get("analytics_summary")
    # Should return a valid summary (possibly with nulls)
    assert summary is not None
    assert "avg_last_24h" in summary
    assert "avg_last_7d" in summary
    assert "datapoints_last_24h" in summary


@pytest.mark.asyncio
async def test_graphql_alert_rules_query(auth_client):
    response = await _post_graphql(auth_client, ALERT_RULES_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"].get("alert_rules"), list)


@pytest.mark.asyncio
async def test_graphql_invalid_query(auth_client):
    response = await _post_graphql(auth_client, "{ invalidField }")
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data


@pytest.mark.asyncio
async def test_graphql_metrics_after_creating_one(auth_client):
    from uuid import uuid4

    payload = {
        "name": "GraphQL Metric",
        "key": "graphql_test_metric",
        "description": "Created for GraphQL test",
        "unit": "count",
        "data_type": "numeric",
        "aggregation_method": "sum",
    }
    response = await auth_client.post("/api/v1/metrics", json=payload)
    assert response.status_code == 201

    resp = await _post_graphql(auth_client, METRICS_QUERY)
    assert resp.status_code == 200
    data = resp.json()
    metrics = data["data"].get("metrics", [])
    names = [m["name"] for m in metrics]
    assert "GraphQL Metric" in names
