from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None
    tenant_id: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    tenant_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


# --- Multi-Tenant ---
class TenantCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    settings_json: Optional[str] = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    domain: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Data Retention ---
class RetentionPolicyCreate(BaseModel):
    metric_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    retention_days: int = 90


class RetentionPolicyResponse(BaseModel):
    id: UUID
    metric_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    retention_days: int
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Webhook Templates ---
class WebhookTemplateCreate(BaseModel):
    name: str
    template_body: str
    description: Optional[str] = None
    template_headers: Optional[str] = None
    content_type: str = "application/json"
    is_default: bool = False


class WebhookTemplateResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    content_type: str
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MetricCreate(BaseModel):
    name: str
    key: str = Field(pattern=r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")
    description: Optional[str] = None
    unit: Optional[str] = None
    data_type: str = "float"
    aggregation_method: str = "avg"


class MetricResponse(BaseModel):
    id: UUID
    name: str
    key: str
    description: Optional[str] = None
    unit: Optional[str] = None
    data_type: str
    aggregation_method: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DataPointRecord(BaseModel):
    value: float
    timestamp: Optional[datetime] = None


class DashboardCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DashboardItemCreate(BaseModel):
    metric_id: UUID
    chart_type: str = "line"
    title: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 6
    height: int = 4


class AlertRuleCreate(BaseModel):
    name: str
    metric_id: UUID
    condition: str = "gt"
    threshold: float
    severity: str = "warning"
    cooldown_minutes: int = 5
    description: Optional[str] = None


class AlertEventResponse(BaseModel):
    id: UUID
    rule_id: UUID
    status: str
    value: float
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DataSourceCreate(BaseModel):
    name: str
    type: str = "api"
    config_json: Optional[str] = None


class AnalyticsQuery(BaseModel):
    metric_id: UUID
    start: datetime
    end: datetime
    interval: str = "1m"


class CompareQuery(BaseModel):
    metric_id: UUID
    current_start: datetime
    current_end: datetime
    previous_start: datetime
    previous_end: datetime

