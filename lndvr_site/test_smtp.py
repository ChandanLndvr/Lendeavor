import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lndvr_site.settings')
django.setup()

from django.core.mail import send_mail

send_mail(
    'Test Email from Lendeavor',
    'This is a test email from your Django SMTP setup.',
    'info@lendeavorusa.com',
    ['chandan@lendeavorusa.com'],
    fail_silently=False,
)

print("Email sent successfully if no error occurred.")
