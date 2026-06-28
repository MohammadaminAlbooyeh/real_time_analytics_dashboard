import httpx
from backend.utils.logger import get_logger

logger = get_logger("webhook_notifier")


async def send_webhook(url: str, payload: dict) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook sent to {url}, status={response.status_code}")
            return True
    except Exception as e:
        logger.error(f"Failed to send webhook: {e}")
        return False
