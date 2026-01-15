from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives


def send_confirmation_email(request, email, code):
    ''' Sends the confirmation email. '''
    ''' Sends the reset password email. '''
    code = str(code)


    # Format the reset code in grups of 3 digits
    formatted_code = (
        f'{code[:3]} {code[3:6]} {code[6:9]} {code[9:]}'
    )

    # Email subject
    subject = 'Confirme o seu registo.'

    # Email body in plain text(only for email clients that don't support HTML)
    text_content = (
        f'Bem vindo á Extreme Way, { email }.\n\n'
        'Para confirmar o seu registo, por favor insira o código código de verificação abaixo:\n\n'
        f'{formatted_code}\n\n'
        'Obrigado!'
    )

    # Email body in HTML
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333;">Bem vindo á Extreme Way, {email}.</h2>
            <p>Para confirmar o seu registo, insira o código de verificação abaixo:</p>

            <!-- Formatted code -->
            <div style="text-align: center; font-size: 32px; font-weight: bold; margin: 20px 0;">
                {formatted_code}
            </div>

            <p></p>
            <p>Obrigado!</p>
        </div>
    </body>
    </html>
    """

    # Create the email message
    email_message = EmailMultiAlternatives(
        subject, text_content, settings.EMAIL_HOST_USER, [email]
    )

    # Add the HTML content to the email
    email_message.attach_alternative(html_content, "text/html")

    # Send the email
    email_message.send()


def send_reset_password_email( email, reset_code):
    ''' Sends the reset password email. '''
    reset_code = str(reset_code)

    user = User.objects.get(email=email)

    # Format the reset code in grups of 3 digits
    formatted_code = (
        f'{reset_code[:3]} {reset_code[3:6]} {reset_code[6:9]} {reset_code[9:]}'
    )

    # Email subject
    subject = 'Redefinição de senha'

    # Email body in plain text(only for email clients that don't support HTML)
    text_content = (
        f'Olá {user.first_name} {user.last_name}, o seu username é { user.username }.\n\n'
        'Para redefinir a sua senha, por favor insira o código abaixo no campo correspondente:\n\n'
        f'{formatted_code}\n\n'
        'Obrigado!'
    )

    # Email body in HTML
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333;">Olá, { user.first_name } { user.last_name }.</h2>
            <p>O seu username é <strong>{user.username}</strong>.</p>
            <p>Para redefinir a sua senha, insira o código de verificação abaixo:</p>

            <!-- Formatted code -->
            <div style="text-align: center; font-size: 32px; font-weight: bold; margin: 20px 0;">
                {formatted_code}
            </div>

            <p>Se você não solicitou esta alteração, por favor ignore este email.</p>
            <p>Obrigado!</p>
        </div>
    </body>
    </html>
    """

    # Create the email message
    email_message = EmailMultiAlternatives(
        subject, text_content, settings.EMAIL_HOST_USER, [email]
    )

    # Add the HTML content to the email
    email_message.attach_alternative(html_content, "text/html")

    # Send the email
    email_message.send()
