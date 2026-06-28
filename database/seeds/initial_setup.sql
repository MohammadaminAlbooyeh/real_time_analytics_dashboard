INSERT INTO users (id, email, username, hashed_password, full_name, is_admin)
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'admin@analytics.local',
    'admin',
    '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5Jq5Jq5Jq5Jq5Jq5Jq5Jq5O',
    'Admin User',
    TRUE
);

INSERT INTO metrics (id, name, key, description, unit, data_type, aggregation_method)
VALUES
    ('b0000000-0000-0000-0000-000000000001', 'Page Views', 'page.views', 'Number of page views', 'count', 'integer', 'sum'),
    ('b0000000-0000-0000-0000-000000000002', 'API Latency', 'api.latency', 'API response time', 'ms', 'float', 'avg'),
    ('b0000000-0000-0000-0000-000000000003', 'Error Rate', 'error.rate', 'Percentage of errored requests', '%', 'float', 'avg'),
    ('b0000000-0000-0000-0000-000000000004', 'Active Users', 'users.active', 'Currently active users', 'count', 'integer', 'sum'),
    ('b0000000-0000-0000-0000-000000000005', 'CPU Usage', 'system.cpu', 'CPU utilization', '%', 'float', 'avg');

INSERT INTO dashboards (id, name, description, owner_id, layout)
VALUES (
    'c0000000-0000-0000-0000-000000000001',
    'System Overview',
    'Main system monitoring dashboard',
    'a0000000-0000-0000-0000-000000000001',
    '{"columns": 12, "rowHeight": 80}'
);
