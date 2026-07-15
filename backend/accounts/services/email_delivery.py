from django.conf import settings
from django.core.mail import send_mail


def send_confirmation_email(email, token):
    send_mail(
        'Confirme seu acesso ao Zyrp',
        f'Confirme seu e-mail usando token={token}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
