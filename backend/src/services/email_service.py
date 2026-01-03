from .email_impl.celery_tasks import send_email_task
from typing import Literal, Optional
class EmailService:
    """
        Class that provides a high-level abstraction for sending emails using Resend API.
    """
    
    @staticmethod
    def send_email(to_mail: str, subject: str, 
                   message: str = 'Welcome to DailySpeakUp!',
                   template: Literal['basic_message', 'welcome', 'passwordless_login', 'confirm_account_deletion'] = 'welcome',
                   code: Optional[str] = None,
                   magic_link: Optional[str] = None) -> None:
        """
            Send an email using Resend API.

            This method takes the recipient's email address and the subject of the email as parameters.
            It retursns nothing.
            
            :param to_mail: Recipient's email address.
            :param subject: Subject of the email.
            :param message: Message you want to send.
            :param template: Email template to use.
            :param code: Optional code for passwordless login.
            :param magic_link: Optional magic link for passwordless login.
        """
        # enqueue email sending task to Celery worker
        send_email_task.delay(to_mail, subject, body_text=message, template=template, code=code, magic_link=magic_link)