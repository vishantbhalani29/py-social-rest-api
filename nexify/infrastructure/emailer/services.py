from typing import Any, Dict

from django.conf import settings
from django.core.mail import EmailMessage


class Mail(EmailMessage):
    """
    A class representing an email message.

    This class extends the Django `EmailMessage` class and provides additional methods for setting email data.

    Attributes:
        subject (str): The subject of the email.
        body (str): The body of the email.
        from_email (str): The sender's email address.
        to (list): A list of recipient email addresses.
        bcc (list): A list of blind carbon copy (BCC) email addresses.
        connection (django.core.mail.backends.base.BaseEmailBackend): The email backend connection.
        attachments (list): A list of email attachments.
        headers (dict): Additional email headers.
        cc (list): A list of carbon copy (CC) email addresses.
        reply_to (list): A list of reply-to email addresses.
        dynamic_template_data (dict): Additional dynamic template data for email templates.
        template_id (str): The ID of the email template to use.

    Methods:
        set_mail_data(subject="", body="", from_email=None, to=[], dynamic_template_data=None, template_id=None):
            Sets the email data attributes.

    """

    def __init__(
        self,
        subject="",
        body="",
        from_email=None,
        to=None,
        bcc=None,
        connection=None,
        attachments=None,
        headers=None,
        cc=None,
        reply_to=None,
    ):
        super().__init__(
            subject,
            body,
            from_email,
            to,
            bcc,
            connection,
            attachments,
            headers,
            cc,
            reply_to,
        )

    def set_mail_data(
        self,
        subject="",
        body="",
        from_email=None,
        to=[],
        dynamic_template_data=None,
        template_id=None,
    ):
        """
        Sets the email data attributes.

        Parameters:
            subject (str): The subject of the email. Defaults to an empty string.
            body (str): The body of the email. Defaults to an empty string.
            from_email (str): The sender's email address. Defaults to None.
            to (list): A list of recipient email addresses. Defaults to an empty list.
            dynamic_template_data (dict): Additional dynamic template data for email templates. Defaults to None.
            template_id (str): The ID of the email template to use. Defaults to None.
        """
        self.subject = subject
        self.body = body
        self.from_email = from_email
        self.to = to
        self.dynamic_template_data = dynamic_template_data
        self.template_id = template_id


class MailerServices:
    """
    A class representing a mailer service.

    This class provides methods for setting up and sending email messages using the `Mail` class.

    Attributes:
        from_email (str): The sender's email address.

    Methods:
        set_mail_instance(): Sets up an instance of the `Mail` class.
        send_mail(email: str, subject: str, template_data: Dict[str, Any]): Sends an email message.

    """

    def __init__(self):
        self.from_email = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"

    def set_mail_instance(self):
        """
        Sets up an instance of the `Mail` class.

        This method initializes the `mail_instance` attribute of the `MailerServices` class with an instance of the `Mail` class.

        """
        self.mail_instance = Mail()

    def send_mail(
        self, email: str, subject: str, template_data: Dict[str, Any], template_id: str
    ):
        """
        Sends an email message.

        Parameters:
            email (str): The recipient's email address.
            subject (str): The subject of the email.
            template_data (Dict[str, Any]): A dictionary containing dynamic template data for the email.
            template_id (str): The ID of the email template to use.

        Raises:
            Exception: If an error occurs while sending the email.

        Returns:
            None

        """
        try:
            self.set_mail_instance()
            self.mail_instance.set_mail_data(
                subject=subject,
                from_email=self.from_email,
                to=[email],
                dynamic_template_data=template_data,
                template_id=template_id,
            )
            self.mail_instance.send(fail_silently=False)
        except Exception as e:
            raise e
