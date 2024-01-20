from django.core.mail import send_mail
from django.conf import settings
import uuid
from perfil.models import EmailConfirmationToken


def send_confirmation_email(user):
    """Send confirmation email."""
    token = str(uuid.uuid4())
    EmailConfirmationToken.objects.create(user=user, token=token)
    send_mail(
        'Confirmação de email',
        f'Olá {user.username},\n\n'
        'Para confirmar o seu email, por favor clique no link abaixo:\n\n'
        f'{settings.FRONTEND_URL}/confirmacao-email/{token}\n\n'
        'Obrigado!',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
