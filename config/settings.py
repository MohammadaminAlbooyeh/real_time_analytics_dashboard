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
    kafka_enabled: bool = False

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

    # --- New Feature Settings ---

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_default: str = "100/minute"

    # HTTPS / TLS
    ssl_enabled: bool = False
    ssl_cert_path: str = "/etc/nginx/ssl/cert.pem"
    ssl_key_path: str = "/etc/nginx/ssl/key.pem"

    # Multi-Tenant
    multi_tenant_enabled: bool = True
    default_tenant: str = "default"

    # Encryption at Rest
    encryption_enabled: bool = False
    encryption_key: Optional[str] = None

    # SAML / SSO
    saml_enabled: bool = False
    saml_idp_metadata_url: Optional[str] = None
    saml_sp_entity_id: str = "analytics-dashboard"
    saml_sp_acs_url: str = "http://localhost:8000/auth/saml/acs"
    saml_sp_x509cert: Optional[str] = None
    saml_sp_private_key: Optional[str] = None

    # Data Retention
    retention_default_days: int = 90
    retention_max_days: int = 365

    # ML / Anomaly
    ml_anomaly_contamination: float = 0.05
    ml_forecast_horizon: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
