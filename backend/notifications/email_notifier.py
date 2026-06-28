from config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger("email_notifier")


async def send_email(to: str, subject: str, body: str) -> bool:
    if not settings.email_enabled:
        logger.debug(f"Email disabled, would send to {to}: {subject}")
        return False
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content
        sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
        mail = Mail(
            from_email=Email(settings.email_from),
            to_emails=To(to),
            subject=subject,
            plain_text_content=Content("text/plain", body),
        )
        response = sg.client.mail.send.post(request_body=mail.get())
        logger.info(f"Email sent to {to}, status={response.status_code}")
        return response.status_code in (200, 201, 202)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
