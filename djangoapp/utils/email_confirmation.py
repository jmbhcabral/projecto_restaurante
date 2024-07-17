from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def send_confirmation_email(self, email, username, token):
    confirm_url = reverse('perfil:confirmar_email', args=[token])
    full_url = f"{self.request.scheme}://{self.request.get_host()}{confirm_url}"

    send_mail(
        'Confirmação de email',
        f'Olá {username},\n\n'
        'Para confirmar o seu email, por favor clique no link abaixo:\n\n'
        f'{full_url}\n\n'
        'Obrigado!',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
