from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
import logging

# Automatically log login, logout, and login failure events across your entire Django app.

logger = logging.getLogger('django_actions')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User logged in: {user.email} from IP {request.META.get('REMOTE_ADDR')}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User logged out: {user.email} from IP {request.META.get('REMOTE_ADDR')}")

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    logger.warning(f"Failed login for {credentials.get('username')} from IP {request.META.get('REMOTE_ADDR')}")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip