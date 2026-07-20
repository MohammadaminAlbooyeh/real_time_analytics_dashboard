import uuid
from datetime import datetime, timezone, timedelta
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.time_series import TimeSeriesDataPoint
from backend.utils.logger import get_logger

logger = get_logger("ml_service")

try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. ML features disabled.")


class MLService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._models: dict[str, object] = {}

    async def detect_anomalies_isolation_forest(
        self, metric_id: uuid.UUID,
        lookback_hours: int = 168,
        contamination: float = 0.05,
    ) -> list[dict]:
        """Detect anomalies using Isolation Forest (advanced anomaly detection)."""
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for Isolation Forest anomaly detection")
            return []

        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=lookback_hours)

        result = await self.session.execute(
            select(TimeSeriesDataPoint)
            .where(TimeSeriesDataPoint.metric_id == metric_id)
            .where(TimeSeriesDataPoint.timestamp >= start)
            .where(TimeSeriesDataPoint.timestamp <= now)
            .order_by(TimeSeriesDataPoint.timestamp.asc())
        )
        points = list(result.scalars().all())

        if len(points) < 10:
            logger.warning(f"Not enough data points ({len(points)}) for anomaly detection")
            return []

        values = np.array([p.value for p in points]).reshape(-1, 1)
        timestamps = [p.timestamp for p in points]

        scaler = StandardScaler()
        values_scaled = scaler.fit_transform(values)

        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        predictions = model.fit_predict(values_scaled)
        anomaly_scores = model.score_samples(values_scaled)

        anomalies = []
        for i, (pred, ts, val) in enumerate(zip(predictions, timestamps, values.flatten())):
            if pred == -1:
                anomalies.append({
                    "timestamp": ts.isoformat(),
                    "value": float(val),
                    "anomaly_score": float(round(anomaly_scores[i], 4)),
                    "severity": "high" if anomaly_scores[i] < np.percentile(anomaly_scores, 5) else "medium",
                })

        logger.info(f"Detected {len(anomalies)} anomalies out of {len(points)} points for metric {metric_id}")
        return anomalies

    async def forecast_values(
        self, metric_id: uuid.UUID,
        forecast_hours: int = 24,
        lookback_hours: int = 336,
    ) -> list[dict]:
        """Forecast future metric values using Random Forest regression."""
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn required for forecasting")
            return []

        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=lookback_hours)

        result = await self.session.execute(
            select(TimeSeriesDataPoint)
            .where(TimeSeriesDataPoint.metric_id == metric_id)
            .where(TimeSeriesDataPoint.timestamp >= start)
            .where(TimeSeriesDataPoint.timestamp <= now)
            .order_by(TimeSeriesDataPoint.timestamp.asc())
        )
        points = list(result.scalars().all())

        if len(points) < 24:
            logger.warning(f"Not enough data points ({len(points)}) for forecasting")
            return []

        X = []
        y = []
        for p in points:
            hour = p.timestamp.hour
            day_of_week = p.timestamp.weekday()
            day_of_month = p.timestamp.day
            month = p.timestamp.month
            X.append([hour, day_of_week, day_of_month, month])
            y.append(p.value)

        X = np.array(X)
        y = np.array(y)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        forecasts = []
        for h in range(1, forecast_hours + 1):
            future_ts = now + timedelta(hours=h)
            future_features = np.array([[
                future_ts.hour, future_ts.weekday(),
                future_ts.day, future_ts.month,
            ]])
            pred = model.predict(future_features)[0]
            residuals = y - model.predict(X)
            std_dev = np.std(residuals)
            forecasts.append({
                "timestamp": future_ts.isoformat(),
                "predicted_value": float(round(pred, 4)),
                "confidence_lower": float(round(pred - 1.96 * std_dev, 4)),
                "confidence_upper": float(round(pred + 1.96 * std_dev, 4)),
            })

        logger.info(f"Generated {len(forecasts)} forecast points for metric {metric_id}")
        return forecasts

    async def get_model_insights(self, metric_id: uuid.UUID) -> dict:
        """Get ML-based insights for a metric: trend, seasonality, volatility."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=30)
        result = await self.session.execute(
            select(func.avg(TimeSeriesDataPoint.value), func.variance(TimeSeriesDataPoint.value))
            .where(TimeSeriesDataPoint.metric_id == metric_id)
            .where(TimeSeriesDataPoint.timestamp >= start)
        )
        agg = result.one()
        mean_val = float(agg[0]) if agg[0] else 0
        variance_val = float(agg[1]) if agg[1] else 0
        return {
            "metric_id": str(metric_id),
            "mean": round(mean_val, 4),
            "volatility": round(float(np.sqrt(variance_val)), 4) if variance_val > 0 else 0,
            "period": "30d",
            "data_quality": "good" if mean_val > 0 else "insufficient_data",
        }