from .celery_app import app
from .sender import ResendEmailSender
from ...api.config import get_settings

settings = get_settings()

@app.task(rate_limit=settings.CELERY_RATE_LIMIT)
def send_email_task(to_mail : str, subject : str, body_text : str, template : str, code : str | None = None, magic_link : str | None = None):
    """
    Celery task for sending emails.

    Args:
        to_mail (str): Receiver's email address.
        subject (str): Subject of the email.
        body_text (str): Body text of the email.
        template (str): Template type ('welcome', 'basic_message',  'passwordless_login', 'confirm_account_deletion').
        code (str, optional): Code for passwordless login.
        magic_link (str, optional): Magic link for passwordless login.
    """
    sender = ResendEmailSender()
    sender.send_email(to_mail, subject, body_text, template, code, magic_link)