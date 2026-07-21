# Webhook Templating

## Overview

The Real-Time Analytics Dashboard supports **custom webhook templating** using the **Jinja2** template engine. This allows you to define reusable templates for webhook payloads, including dynamic headers and body content, making it easy to integrate with any external system.

### Template Architecture

```
┌──────────────┐    Create/Manage    ┌─────────────────────┐
│  Admin User   │ ────────────────▶│  Webhook Template    │
│              │                   │  Service             │
│              │                   │  (Jinja2 rendering)  │
└──────────────┘                   └──────────┬──────────┘
                                              │
                    ┌─────────────────────────┴────────────┐
                    │                                      │
            ┌───────▼────────┐                    ┌───────▼────────┐
            │  Template Body  │                    │ Template       │
            │  (Jinja2)       │                    │ Headers (JSON) │
            └────────────────┘                    └────────────────┘
                                              │
                    ┌─────────────────────────┘
                    ▼
            ┌────────────────┐
            │ Rendered       │
            │ Webhook Payload│
            └────────────────┘
```

### Key Features

- **Jinja2 Templates**: Full Jinja2 syntax support (variables, filters, conditionals)
- **Custom Headers**: Dynamic HTTP headers per template
- **Content Type**: Configurable per template (JSON, XML, form-encoded)
- **Default Templates**: Set a default template for all webhooks
- **CRUD Management**: Create, read, update, and delete templates via API

---

## Creating Templates with Jinja2

### Template Model

| Field              | Type      | Description                                 |
|--------------------|-----------|---------------------------------------------|
| `id`               | UUID      | Auto-generated unique identifier            |
| `name`             | String    | Template name (required)                    |
| `description`      | String    | Optional description                        |
| `template_body`    | Text      | Jinja2 template for the webhook body        |
| `template_headers` | String    | JSON template for HTTP headers              |
| `content_type`     | String    | Content-Type header (default: application/json)|
| `is_default`       | Boolean   | Whether this is the default template        |
| `created_at`       | DateTime  | Timestamp of creation                       |
| `updated_at`       | DateTime  | Timestamp of last update                    |

### Basic Template Example

A simple JSON webhook template:

```jinja
{
  "event": "{{ event_type }}",
  "message": "{{ message }}",
  "timestamp": "{{ timestamp }}",
  "severity": "{{ severity }}",
  "value": {{ value }}
}
```

### Template with Conditional Logic

```jinja
{
  "event": "{{ event_type }}",
  "message": "{{ message }}",
  {% if severity == "critical" %}
  "priority": 1,
  "notify": true
  {% else %}
  "priority": 3,
  "notify": false
  {% endif %}
  "timestamp": "{{ timestamp }}"
}
```

### Template with Custom Headers

The `template_headers` field is a JSON string that can also use Jinja2 syntax:

```json
{
  "X-Event-Type": "{{ event_type }}",
  "X-Source": "analytics-dashboard",
  "Authorization": "Bearer {{ api_token }}"
}
```

---

## Template Variables and Context

### Standard Context Variables

When rendering a template, the following variables are available in the context:

| Variable      | Type   | Description                            |
|---------------|--------|----------------------------------------|
| `event_type`  | String | Type of event (e.g., "alert", "metric")|
| `message`     | String | Event description or message           |
| `timestamp`   | String | ISO 8601 timestamp of the event        |
| `severity`    | String | Severity level (e.g., "critical", "warning") |
| `value`       | Float  | Metric value or threshold value        |
| `metric_name` | String | Name of the associated metric          |
| `metric_id`   | String | UUID of the associated metric          |
| `rule_name`   | String | Name of the alert rule (if applicable) |
| `tenant_id`   | String | Tenant identifier (if multi-tenant)    |
| `api_token`   | String | API token for authentication           |

### Custom Context

Additional context variables can be passed when rendering:

```python
context = {
    "event_type": "alert_triggered",
    "message": "CPU usage exceeded 90%",
    "severity": "critical",
    "value": 95.5,
    "custom_field": "any_value",
}
```

---

## Default Templates

### Setting a Default Template

```python
template = await service.create_template(
    name="Default Alert Template",
    description="Default template for all webhook alerts",
    template_body='{"event": "{{ event_type }}", "message": "{{ message }}"}',
    is_default=True,
)
```

### Retrieving the Default Template

```python
default = await service.get_default_template()
```

When a default template is set, it can be used as the fallback for webhook notifications that don't specify a custom template.

---

## API Endpoints

All webhook template endpoints are under **`/api/v1/admin`** and require admin privileges.

### Create Template

```
POST /api/v1/admin/webhook-templates
```

**Request Body:**
```json
{
  "name": "Slack Alert Template",
  "description": "Formatted alerts for Slack",
  "template_body": "{\n  \"text\": \"*{{ severity|upper }}*: {{ message }}\\nEvent: {{ event_type }}\\nTime: {{ timestamp }}\"\n}",
  "template_headers": "{\"Content-Type\": \"application/json\"}",
  "content_type": "application/json",
  "is_default": false
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Slack Alert Template",
  "description": "Formatted alerts for Slack",
  "content_type": "application/json",
  "is_default": false,
  "created_at": "2026-07-21T00:00:00+00:00"
}
```

### List Templates

```
GET /api/v1/admin/webhook-templates?skip=0&limit=100
```

### Get Template

```
GET /api/v1/admin/webhook-templates/{template_id}
```

### Render Template

```
POST /api/v1/admin/webhook-templates/{template_id}/render
```

**Request Body:**
```json
{
  "event_type": "alert_triggered",
  "message": "CPU usage high",
  "severity": "critical",
  "value": 95.5
}
```

**Response (rendered Jinja2 output):**
```json
{
  "body": "{\n  \"text\": \"*CRITICAL*: CPU usage high\\nEvent: alert_triggered\\nTime: 2026-07-21T12:00:00\"\n}",
  "headers": {
    "Content-Type": "application/json"
  },
  "content_type": "application/json"
}
```

### Update Template

```
PUT /api/v1/admin/webhook-templates/{template_id}
```

**Query Parameters:**
```
name=New Name&description=Updated description
```

### Delete Template

```
DELETE /api/v1/admin/webhook-templates/{template_id}
```

**Response:**
```json
{
  "status": "deleted"
}
```

---

## Using Templates with Webhook Notifications

The webhook template service integrates with the notification system. When sending a webhook notification:

1. The system looks up the configured template (or uses the default)
2. The template is rendered with the event context
3. The rendered payload is sent to the webhook URL

```python
from backend.services.webhook_template_service import WebhookTemplateService

service = WebhookTemplateService(session)

# Get a template and render it
template = await service.get_template(template_id)
rendered = await service.render_template(template_id, {
    "event_type": "alert_triggered",
    "message": "CPU at 95%",
    "severity": "critical",
    "value": 95.0,
    "timestamp": "2026-07-21T12:00:00Z",
})

# rendered["body"] - The rendered webhook payload
# rendered["headers"] - Dynamic HTTP headers
# rendered["content_type"] - Content-Type to use
```

---

## Best Practices

1. **Use Descriptive Names**: Give templates clear names that describe their purpose
2. **Test Templates First**: Use the render endpoint to test templates before using them
3. **Handle Missing Variables**: Use Jinja2's `default()` filter for optional fields
4. **Keep Templates Simple**: Complex logic is better handled in the application code
5. **Secure Templates**: Avoid exposing sensitive data in template headers

---

## Related Documentation

- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Full API reference
- [ALERT_RULES.md](./ALERT_RULES.md) - Alert configuration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
