''' Reset Password Email '''
import uuid
from django.conf import settings
from django.core.mail import send_mail
from perfil.models import PasswordResetToken


def reset_password_email(user):
    """
    Send reset password email to user.

    """
    token = str(uuid.uuid4())
    PasswordResetToken.objects.create(user=user, token=token)
    send_mail(
        'Recuperação de password',
        f'Olá {user.username},\n\n'
        'Para recuperar a sua password, por favor clique no link abaixo:\n\n'
        f'{settings.FRONTEND_URL}/perfil/reset_password/{token}\n\n'
        'Obrigado!',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
