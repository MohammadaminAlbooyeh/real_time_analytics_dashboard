INSERT INTO time_series_data (id, metric_id, timestamp, value)
SELECT
    gen_random_uuid(),
    'b0000000-0000-0000-0000-000000000001',
    generate_series(
        NOW() - INTERVAL '7 days',
        NOW(),
        INTERVAL '5 minutes'
    ) AS timestamp,
    floor(random() * 1000 + 100)::float AS value;

INSERT INTO time_series_data (id, metric_id, timestamp, value)
SELECT
    gen_random_uuid(),
    'b0000000-0000-0000-0000-000000000002',
    generate_series(
        NOW() - INTERVAL '7 days',
        NOW(),
        INTERVAL '1 minute'
    ) AS timestamp,
    floor(random() * 200 + 10)::float AS value;

INSERT INTO time_series_data (id, metric_id, timestamp, value)
SELECT
    gen_random_uuid(),
    'b0000000-0000-0000-0000-000000000003',
    generate_series(
        NOW() - INTERVAL '7 days',
        NOW(),
        INTERVAL '5 minutes'
    ) AS timestamp,
    round((random() * 5)::numeric, 2)::float AS value;

INSERT INTO alert_rules (id, name, metric_id, condition, threshold, severity, enabled)
VALUES
    ('d0000000-0000-0000-0000-000000000001', 'High Error Rate', 'b0000000-0000-0000-0000-000000000003', 'gt', 3.0, 'critical', TRUE),
    ('d0000000-0000-0000-0000-000000000002', 'High Latency', 'b0000000-0000-0000-0000-000000000002', 'gt', 150.0, 'warning', TRUE);
