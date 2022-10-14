from django.conf import settings
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.conf import settings

def sendMail(to, template, content):
    html_content = render_to_string(f'account/email/{template}.html', content)
    text_content = render_to_string(f'account/email/{template}.txt', content)
    message = EmailMultiAlternatives(content['subject'], text_content, settings.EMAIL_HOST_USER, [to])
    message.attach_alternative(html_content, 'text/html')
    message.send()

def send_activation_email(request, email, code):
    content = {
        'subject': _('URL Shorty - Profile Activation'),
        'uri'    : request.build_absolute_uri(reverse('account:activate', kwargs={'code': code})), 
    }
    sendMail(email, 'profileActivation', content)

def send_userNameForgot_email(email, username):
    context = {
        'subject': _('URL Shorty - Remind username'),
        'username': username,
    }
    sendMail(email, 'userNameForgot', context)

def send_passwordReset_email(request, email, token, uid):
    context = {
        'subject': _('URL Shorty - Restore password'),
        'uri': request.build_absolute_uri(reverse('account:restore_password_confirm', kwargs={'uidb64': uid, 'token': token})),
    }

    sendMail(email, 'PasswordReset', context)