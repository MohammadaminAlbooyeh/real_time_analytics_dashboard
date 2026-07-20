import httpx
from backend.utils.logger import get_logger

logger = get_logger("webhook_notifier")


async def send_webhook(url: str, payload: dict, template_id: str | None = None) -> bool:
    try:
        content = payload
        headers = {"Content-Type": "application/json"}

        # If a template is specified, render the payload through it
        if template_id:
            from sqlalchemy.ext.asyncio import AsyncSession
            from config.database_config import async_session_factory
            from backend.services.webhook_template_service import WebhookTemplateService

            async with async_session_factory() as session:
                service = WebhookTemplateService(session)
                rendered = await service.render_template(template_id, payload)
                if rendered:
                    content = rendered["body"]
                    headers = rendered["headers"]
                    headers.setdefault("Content-Type", rendered["content_type"])

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=content, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook sent to {url}, status={response.status_code}")
            return True
    except Exception as e:
        logger.error(f"Failed to send webhook: {e}")
        return False

