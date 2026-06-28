from config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger("slack_notifier")


async def send_slack_message(channel: str, message: str) -> bool:
    if not settings.slack_enabled:
        logger.debug(f"Slack disabled, would send to {channel}: {message}")
        return False
    try:
        from slack_sdk.web.async_client import AsyncWebClient
        client = AsyncWebClient(token=settings.slack_bot_token)
        response = await client.chat_postMessage(channel=channel, text=message)
        logger.info(f"Slack message sent to {channel}")
        return response["ok"]
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        return False
