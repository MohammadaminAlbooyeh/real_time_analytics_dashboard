import pytest
from uuid import uuid4
from backend.services.webhook_template_service import WebhookTemplateService


SAMPLE_TEMPLATE = '{"event": "{{ event_type }}", "message": "{{ message }}", "timestamp": "{{ timestamp }}"}'
SAMPLE_HEADERS = '{"X-Custom-Header": "{{ header_value }}"}'


@pytest.mark.asyncio
async def test_create_template(db_session):
    service = WebhookTemplateService(db_session)
    tmpl = await service.create_template(
        name="Test Template",
        template_body=SAMPLE_TEMPLATE,
    )
    assert tmpl.id is not None
    assert tmpl.name == "Test Template"
    assert tmpl.content_type == "application/json"
    assert tmpl.is_default is False


@pytest.mark.asyncio
async def test_create_template_with_all_fields(db_session):
    service = WebhookTemplateService(db_session)
    tmpl = await service.create_template(
        name="Full Template",
        template_body=SAMPLE_TEMPLATE,
        description="A full webhook template",
        template_headers=SAMPLE_HEADERS,
        content_type="application/json",
        is_default=True,
    )
    assert tmpl.name == "Full Template"
    assert tmpl.description == "A full webhook template"
    assert tmpl.template_headers == SAMPLE_HEADERS
    assert tmpl.is_default is True


@pytest.mark.asyncio
async def test_list_templates(db_session):
    service = WebhookTemplateService(db_session)
    await service.create_template(name="Alpha", template_body=SAMPLE_TEMPLATE)
    await service.create_template(name="Beta", template_body=SAMPLE_TEMPLATE)

    templates = await service.list_templates()
    assert len(templates) == 2


@pytest.mark.asyncio
async def test_list_templates_empty(db_session):
    service = WebhookTemplateService(db_session)
    templates = await service.list_templates()
    assert len(templates) == 0


@pytest.mark.asyncio
async def test_get_template(db_session):
    service = WebhookTemplateService(db_session)
    created = await service.create_template(
        name="Get Me", template_body=SAMPLE_TEMPLATE
    )

    found = await service.get_template(created.id)
    assert found is not None
    assert found.name == "Get Me"


@pytest.mark.asyncio
async def test_get_template_not_found(db_session):
    service = WebhookTemplateService(db_session)
    result = await service.get_template(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_default_template(db_session):
    service = WebhookTemplateService(db_session)
    await service.create_template(
        name="Non Default", template_body=SAMPLE_TEMPLATE, is_default=False
    )
    default = await service.create_template(
        name="Default One", template_body=SAMPLE_TEMPLATE, is_default=True
    )

    found = await service.get_default_template()
    assert found is not None
    assert found.name == "Default One"
    assert found.is_default is True


@pytest.mark.asyncio
async def test_get_default_template_none(db_session):
    service = WebhookTemplateService(db_session)
    result = await service.get_default_template()
    assert result is None


@pytest.mark.asyncio
async def test_render_template(db_session):
    service = WebhookTemplateService(db_session)
    tmpl = await service.create_template(
        name="Render Test",
        template_body='{"event": "{{ event_type }}", "value": {{ value }}}',
    )

    context = {"event_type": "page_view", "value": 42}
    result = await service.render_template(tmpl.id, context)
    assert result is not None
    assert result["content_type"] == "application/json"
    assert '"page_view"' in result["body"]
    assert "42" in result["body"]


@pytest.mark.asyncio
async def test_render_template_with_headers(db_session):
    service = WebhookTemplateService(db_session)
    tmpl = await service.create_template(
        name="Headers Test",
        template_body='{"ok": true}',
        template_headers='{"X-Source": "{{ source }}"}',
    )

    result = await service.render_template(tmpl.id, {"source": "dashboard"})
    assert result is not None
    assert result["headers"].get("X-Source") == "dashboard"


@pytest.mark.asyncio
async def test_render_template_not_found(db_session):
    service = WebhookTemplateService(db_session)
    result = await service.render_template(uuid4(), {"key": "val"})
    assert result is None


@pytest.mark.asyncio
async def test_update_template(db_session):
    service = WebhookTemplateService(db_session)
    created = await service.create_template(
        name="Old Name", template_body=SAMPLE_TEMPLATE
    )

    updated = await service.update_template(created.id, name="New Name")
    assert updated is not None
    assert updated.name == "New Name"
    assert updated.template_body == SAMPLE_TEMPLATE


@pytest.mark.asyncio
async def test_update_template_not_found(db_session):
    service = WebhookTemplateService(db_session)
    result = await service.update_template(uuid4(), name="Noop")
    assert result is None


@pytest.mark.asyncio
async def test_delete_template(db_session):
    service = WebhookTemplateService(db_session)
    created = await service.create_template(
        name="Delete Me", template_body=SAMPLE_TEMPLATE
    )

    deleted = await service.delete_template(created.id)
    assert deleted is True

    found = await service.get_template(created.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_template_not_found(db_session):
    service = WebhookTemplateService(db_session)
    result = await service.delete_template(uuid4())
    assert result is False
