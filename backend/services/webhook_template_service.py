import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.webhook_template import WebhookTemplate
from backend.utils.logger import get_logger
from jinja2 import Template

logger = get_logger("webhook_template_service")


class WebhookTemplateService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_template(
        self, name: str, template_body: str,
        description: str | None = None,
        template_headers: str | None = None,
        content_type: str = "application/json",
        is_default: bool = False,
    ) -> WebhookTemplate:
        tmpl = WebhookTemplate(
            name=name,
            description=description,
            template_body=template_body,
            template_headers=template_headers,
            content_type=content_type,
            is_default=is_default,
        )
        self.session.add(tmpl)
        await self.session.flush()
        logger.info(f"Created webhook template {tmpl.id}")
        return tmpl

    async def list_templates(self, skip: int = 0, limit: int = 100) -> list[WebhookTemplate]:
        result = await self.session.execute(
            select(WebhookTemplate).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_template(self, template_id: uuid.UUID) -> WebhookTemplate | None:
        result = await self.session.execute(
            select(WebhookTemplate).where(WebhookTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_default_template(self) -> WebhookTemplate | None:
        result = await self.session.execute(
            select(WebhookTemplate).where(WebhookTemplate.is_default == True)
        )
        return result.scalar_one_or_none()

    async def render_template(self, template_id: uuid.UUID, context: dict) -> dict | None:
        tmpl = await self.get_template(template_id)
        if not tmpl:
            return None
        jinja_template = Template(tmpl.template_body)
        rendered_body = jinja_template.render(**context)
        headers = {}
        if tmpl.template_headers:
            jinja_headers = Template(tmpl.template_headers)
            import json
            headers = json.loads(jinja_headers.render(**context))
        return {
            "body": rendered_body,
            "headers": headers,
            "content_type": tmpl.content_type,
        }

    async def update_template(
        self, template_id: uuid.UUID, **kwargs
    ) -> WebhookTemplate | None:
        tmpl = await self.get_template(template_id)
        if not tmpl:
            return None
        for key, value in kwargs.items():
            if hasattr(tmpl, key) and value is not None:
                setattr(tmpl, key, value)
        await self.session.flush()
        return tmpl

    async def delete_template(self, template_id: uuid.UUID) -> bool:
        tmpl = await self.get_template(template_id)
        if not tmpl:
            return False
        await self.session.delete(tmpl)
        await self.session.flush()
        return True
