from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Real-Time Analytics Dashboard"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/analytics"
    database_sync_url: str = "postgresql://postgres:postgres@localhost:5432/analytics"

    redis_url: str = "redis://localhost:6379/0"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "analytics-consumer"

    websocket_heartbeat_interval: int = 30

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    email_enabled: bool = False
    email_from: Optional[str] = None
    sendgrid_api_key: Optional[str] = None

    slack_enabled: bool = False
    slack_bot_token: Optional[str] = None

    prometheus_enabled: bool = True

    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
