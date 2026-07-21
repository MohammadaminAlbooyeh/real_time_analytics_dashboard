# Machine Learning Features

## Overview

The Real-Time Analytics Dashboard integrates **scikit-learn** to provide advanced machine learning capabilities for time-series data analysis. These features enable anomaly detection, future value forecasting, and statistical insights — all accessible via REST API and GraphQL.

### Available ML Capabilities

| Feature                  | Algorithm                    | Description                                 |
|--------------------------|------------------------------|---------------------------------------------|
| Anomaly Detection        | Isolation Forest             | Identify outliers in metric data            |
| Time Series Forecasting  | Random Forest Regressor      | Predict future metric values                |
| Model Insights           | Statistical Analysis         | Trend, volatility, and data quality metrics |

### ML Service Architecture

```
┌──────────┐    HTTP/GraphQL     ┌──────────────────┐
│  Client   │ ──────────────────▶│   ML Service     │
└──────────┘                     │  (backend/services│
                                 │   /ml_service.py) │
                                 └────────┬─────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          │                               │
                    ┌─────▼──────┐                 ┌──────▼──────┐
                    │ PostgreSQL │                 │ scikit-learn │
                    │ (Time-Series)│                │ (ML Models)  │
                    └────────────┘                 └─────────────┘
```

### Prerequisites

The ML features require `scikit-learn` (installed via `requirements.txt`). If the library is not available, the service gracefully degrades and returns empty results.

---

## Anomaly Detection with Isolation Forest

### Overview

The system uses **Isolation Forest**, an unsupervised learning algorithm that identifies anomalies by isolating outliers in the data. It's particularly effective for high-dimensional datasets and works well with time-series metric data.

### How It Works

1. Data points are retrieved from the time-series database for a given metric
2. Values are normalized using `StandardScaler`
3. The Isolation Forest model is trained with configurable contamination rate
4. Points classified as `-1` (outliers) are returned as anomalies with severity scores

### API Endpoint

```
GET /api/v1/admin/ml/anomalies/{metric_id}
```

**Query Parameters:**

| Parameter        | Default | Description                                  |
|------------------|---------|----------------------------------------------|
| `lookback_hours` | `168`   | How many hours of history to analyze (7 days)|
| `contamination`  | `0.05`  | Expected proportion of outliers (0.0 - 0.5)  |

**Response:**
```json
{
  "metric_id": "uuid",
  "count": 3,
  "anomalies": [
    {
      "timestamp": "2026-07-20T14:30:00+00:00",
      "value": 5234.12,
      "anomaly_score": -0.2456,
      "severity": "high"
    }
  ]
}
```

### Example cURL

```bash
curl -X GET "http://localhost:8000/api/v1/admin/ml/anomalies/{metric_id}?lookback_hours=168&contamination=0.05" \
  -H "Authorization: Bearer <token>"
```

### GraphQL Query

```graphql
query {
  anomalies(metricId: "uuid", lookbackHours: 168) {
    timestamp
    value
    anomalyScore
    severity
  }
}
```

### Minimum Data Requirement

At least **10 data points** are required for anomaly detection.

---

## Time Series Forecasting with Random Forest

### Overview

The system uses **Random Forest Regressor** to forecast future metric values. The model is trained on historical time-series features including hour of day, day of week, day of month, and month.

### How It Works

1. Historical data points (default: 336 hours / 14 days) are retrieved
2. Feature engineering extracts temporal features from timestamps
3. A Random Forest model (100 estimators) is trained on the data
4. Future timestamps are generated and predicted with confidence intervals
5. Results include 95% confidence intervals (mean ± 1.96 × std)

### API Endpoint

```
GET /api/v1/admin/ml/forecast/{metric_id}
```

**Query Parameters:**

| Parameter        | Default | Description                                  |
|------------------|---------|----------------------------------------------|
| `forecast_hours` | `24`    | Number of future hours to predict            |
| `lookback_hours` | `336`   | Hours of historical data for training (14d)  |

**Response:**
```json
{
  "metric_id": "uuid",
  "count": 24,
  "forecasts": [
    {
      "timestamp": "2026-07-22T00:00:00+00:00",
      "predicted_value": 150.2345,
      "confidence_lower": 142.1234,
      "confidence_upper": 158.3456
    }
  ]
}
```

### Example cURL

```bash
curl -X GET "http://localhost:8000/api/v1/admin/ml/forecast/{metric_id}?forecast_hours=24&lookback_hours=336" \
  -H "Authorization: Bearer <token>"
```

### GraphQL Query

```graphql
query {
  forecasts(metricId: "uuid", forecastHours: 24) {
    timestamp
    predictedValue
    confidenceLower
    confidenceUpper
  }
}
```

### Minimum Data Requirement

At least **24 data points** are required for forecasting.

---

## Model Insights

### Overview

Provides statistical analysis of metric data over a 30-day period, including mean value, volatility (standard deviation), and data quality assessment.

### API Endpoint

```
GET /api/v1/admin/ml/insights/{metric_id}
```

**Response:**
```json
{
  "metric_id": "uuid",
  "mean": 152.3456,
  "volatility": 23.4567,
  "period": "30d",
  "data_quality": "good"
}
```

| Field          | Type    | Description                                    |
|----------------|---------|------------------------------------------------|
| `metric_id`    | String  | UUID of the metric                             |
| `mean`         | Float   | Average value over the 30-day period           |
| `volatility`   | Float   | Standard deviation (measure of variability)    |
| `period`       | String  | Analysis period (fixed at "30d")               |
| `data_quality` | String  | "good" or "insufficient_data"                  |

---

## Configuration Options

| Environment Variable            | Default | Description                                      |
|---------------------------------|---------|--------------------------------------------------|
| `ML_ANOMALY_CONTAMINATION`      | `0.05`  | Default contamination rate for Isolation Forest  |
| `ML_FORECAST_HORIZON`           | `24`    | Default forecast horizon in hours                |

### Application Settings

```python
# config/settings.py
ml_anomaly_contamination: float = 0.05
ml_forecast_horizon: int = 24
```

---

## Legacy Anomaly Detector

In addition to the ML-powered Isolation Forest, the system includes a **basic stream-based anomaly detector** in `backend/processors/anomaly_detector.py` using Z-score analysis:

| Feature              | Z-Score Detector          | Isolation Forest          |
|----------------------|---------------------------|---------------------------|
| Algorithm            | Moving Z-score            | Unsupervised ensemble     |
| State                | In-memory (streaming)     | Stateless (query-based)   |
| Use Case             | Real-time stream process  | Historical batch analysis |
| Min Data Points      | 5                         | 10                        |

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Full API reference
- [METRIC_DEFINITIONS.md](./METRIC_DEFINITIONS.md) - Creating and managing metrics
- [DATA_PIPELINE.md](./DATA_PIPELINE.md) - Data pipeline overview
