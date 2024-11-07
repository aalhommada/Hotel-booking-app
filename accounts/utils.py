from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_welcome_email(user):
    subject = 'Welcome to HotelEase'
    html_message = render_to_string('accounts/emails/welcome.html', {
        'user': user
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message
    )

def send_password_reset_email(user, reset_url):
    subject = 'Reset Your Password'
    html_message = render_to_string('accounts/emails/password_reset.html', {
        'user': user,
        'reset_url': reset_url
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message
    )