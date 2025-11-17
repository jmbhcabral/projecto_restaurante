from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_email_notification(to: str, subject: str, template_name: str, context: dict):
    if not to:
        return

    html = render_to_string(template_name, context)
    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to],
        html_message=html,
    )
