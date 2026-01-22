from ...api.config import get_settings
from .email_template import basic_html_message, place_holder, welcome_message, passwordless_login, delete_account_message
import resend

class ResendEmailSender:
    """
        This class is an implementation of a e-mail sender based on Resend API. 
    """
    def __init__(self, resend_api_key : str | None = None, from_email: str | None = None) -> None:
        self._settings = get_settings()
        self.api_key = resend_api_key if resend_api_key else self._settings.RESEND_API_KEY
        self.from_email = from_email if from_email else self._settings.RESEND_FROM_EMAIL

    def send_email(self, to_email: str, subject: str, body_text: str, template: str | None = None, code: str | None = None, magic_link: str | None = None) -> None:
        """
            Method for sending an e-mail using Resend API and basic DailySpeakUp mailig template.
            
            :param to_email: reciever's email
            :param subject: subject of the email being sent
            :param body_text: text used as a main message in the body of the DailySpeakUp mailing template
            :param template: template type to use
            :param code: optional code for passwordless login
            :param magic_link: optional magic link for passwordless login
        """
        resend.api_key = self.api_key

        if template is None or template == 'welcome':
            html = welcome_message()
        elif template == 'basic_message':
            html = basic_html_message().replace(place_holder(), body_text)
        elif template == 'confirm_account_deletion':
            html = delete_account_message()
        elif template == 'passwordless_login':
            html = passwordless_login()
            if code:
                html = html.replace('REPLACE_WITH_CODE', code)
            if magic_link:
                html = html.replace('REPLACE_WITH_MAGIC_LINK', magic_link)
        else:
            html = basic_html_message().replace(place_holder(), body_text)


        params: resend.Emails.SendParams = {
            "from" : f"DailySpeakUp <{self.from_email}>",
            "to" : [to_email],
            "subject" : subject,
            "html" : html
        }

        email = resend.Emails.send(params)