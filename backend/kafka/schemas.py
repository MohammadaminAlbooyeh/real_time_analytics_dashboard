RAW_DATA_SCHEMA = {
    "type": "record",
    "name": "RawData",
    "fields": [
        {"name": "source_id", "type": "string"},
        {"name": "metric_key", "type": "string"},
        {"name": "value", "type": "double"},
        {"name": "timestamp", "type": "string"},
        {"name": "tags", "type": {"type": "map", "values": "string"}, "default": {}},
    ],
}

AGGREGATED_DATA_SCHEMA = {
    "type": "record",
    "name": "AggregatedData",
    "fields": [
        {"name": "metric_key", "type": "string"},
        {"name": "window_start", "type": "string"},
        {"name": "window_end", "type": "string"},
        {"name": "avg", "type": "double"},
        {"name": "min", "type": "double"},
        {"name": "max", "type": "double"},
        {"name": "count", "type": "int"},
        {"name": "sum", "type": "double"},
    ],
}

ALERT_SCHEMA = {
    "type": "record",
    "name": "Alert",
    "fields": [
        {"name": "rule_id", "type": "string"},
        {"name": "metric_key", "type": "string"},
        {"name": "value", "type": "double"},
        {"name": "threshold", "type": "double"},
        {"name": "severity", "type": "string"},
        {"name": "message", "type": "string"},
        {"name": "timestamp", "type": "string"},
    ],
}
