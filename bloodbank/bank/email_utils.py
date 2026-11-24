
from django.conf import settings
from django.core.mail import send_mail


def send_notification_email(to_email, subject, message):
    """
    Send an email when an address is available.
    Returns True if Django reports that the email was accepted.
    """
    if not to_email or not to_email.strip():
        return False

    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email.strip()],
            fail_silently=False,
        )
        return sent == 1
    except Exception:
        # Keep an email failure from breaking the main workflow.
        return False

