"""Unit tests for the platform all-events consumer."""

import pytest

from backend.kafka.all_events_consumer import (
    AllEventsConsumer,
    ORDER_CANCELLED,
    ORDER_CREATED,
    ORDER_CONFIRMED,
    PAYMENT_SUCCEEDED,
)
from backend.models.metric import Metric
from backend.models.time_series import TimeSeriesDataPoint
from sqlalchemy import select


@pytest.mark.asyncio
async def test_order_confirmed_records_count_metric(db_session):
    consumer = AllEventsConsumer()

    await consumer._process(
        db_session,
        ORDER_CONFIRMED,
        {
            "orderId": "o1",
            "userId": "u1",
            "items": [
                {"productId": "p1", "name": "Laptop", "unitPrice": 1200, "quantity": 1}
            ],
        },
    )
    await db_session.commit()

    metric = (
        await db_session.execute(
            select(Metric).where(Metric.key == "sales.orders.confirmed")
        )
    ).scalar_one()
    points = (
        (
            await db_session.execute(
                select(TimeSeriesDataPoint).where(
                    TimeSeriesDataPoint.metric_id == metric.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(points) == 1
    assert points[0].value == 1.0


@pytest.mark.asyncio
async def test_payment_succeeded_records_revenue(db_session):
    consumer = AllEventsConsumer()

    await consumer._process(
        db_session,
        PAYMENT_SUCCEEDED,
        {"orderId": "o2", "transactionId": "t2", "amount": 250.5},
    )
    await db_session.commit()

    metric = (
        await db_session.execute(select(Metric).where(Metric.key == "sales.revenue"))
    ).scalar_one()
    points = (
        (
            await db_session.execute(
                select(TimeSeriesDataPoint).where(
                    TimeSeriesDataPoint.metric_id == metric.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(points) == 1
    assert points[0].value == 250.5


@pytest.mark.asyncio
async def test_order_created_records_count_and_gmv(db_session):
    consumer = AllEventsConsumer()

    await consumer._process(
        db_session,
        ORDER_CREATED,
        {
            "orderId": "o3",
            "userId": "u3",
            "items": [],
            "totalAmount": 999.0,
        },
    )
    await db_session.commit()

    count_metric = (
        await db_session.execute(
            select(Metric).where(Metric.key == "sales.orders.created")
        )
    ).scalar_one()
    gmv_metric = (
        await db_session.execute(
            select(Metric).where(Metric.key == "sales.gmv.created")
        )
    ).scalar_one()

    assert (
        await db_session.execute(
            select(TimeSeriesDataPoint).where(
                TimeSeriesDataPoint.metric_id == count_metric.id
            )
        )
    ).scalars().all()[0].value == 1.0
    assert (
        await db_session.execute(
            select(TimeSeriesDataPoint).where(
                TimeSeriesDataPoint.metric_id == gmv_metric.id
            )
        )
    ).scalars().all()[0].value == 999.0


@pytest.mark.asyncio
async def test_order_cancelled_records_count_metric(db_session):
    consumer = AllEventsConsumer()

    await consumer._process(
        db_session, ORDER_CANCELLED, {"orderId": "o4", "reason": "payment failed"}
    )
    await db_session.commit()

    metric = (
        await db_session.execute(
            select(Metric).where(Metric.key == "sales.orders.cancelled")
        )
    ).scalar_one()
    points = (
        (
            await db_session.execute(
                select(TimeSeriesDataPoint).where(
                    TimeSeriesDataPoint.metric_id == metric.id
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(points) == 1
