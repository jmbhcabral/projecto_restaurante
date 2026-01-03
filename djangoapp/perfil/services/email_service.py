""" Modulo de geração de emails"""
# djangoapp/perfil/services/email_service.py
from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def _format_code_6(code: str) -> str:
    # English comment: group as "123 456"
    c = (code or "").strip()
    if len(c) != 6:
        return c
    return f"{c[:3]} {c[3:]}"


def send_signup_code_email(*, email: str, code: str) -> None:
    """
    New flow: signup verification email (6-digit code).
    """
    formatted_code = _format_code_6(str(code))

    subject = "Código de verificação — confirmar registo"

    text_content = (
        f"Olá,\n\n"
        f"Bem-vindo à Extreme Way.\n"
        f"Para confirmares o teu registo, introduz este código:\n\n"
        f"{formatted_code}\n\n"
        f"Se não foste tu, ignora este email.\n"
        f"Obrigado!"
    )

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 640px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
          <h2 style="color:#222; margin-top: 0;">Confirma o teu registo</h2>
          <p style="color:#444; line-height: 1.5;">
            Bem-vindo à <strong>Extreme Way</strong>. Para confirmares o teu registo, introduz o código abaixo:
          </p>

          <div style="text-align:center; margin: 22px 0;">
            <div style="display:inline-block; padding: 14px 22px; border-radius: 10px; background: #f7f7f7; letter-spacing: 3px; font-size: 32px; font-weight: 700; color:#111;">
              {formatted_code}
            </div>
          </div>

          <p style="color:#666; line-height: 1.5; margin-bottom: 0;">
            Se não foste tu que pediste este código, podes ignorar este email.
          </p>
        </div>

        <p style="text-align:center; color:#999; font-size: 12px; margin-top: 14px;">
          Extreme Way
        </p>
      </body>
    </html>
    """

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


def send_signup_verified_email(*, email: str) -> None:
    """
    Optional: confirmation after successful verification.
    """
    subject = "Registo confirmado com sucesso"

    text_content = (
        "Olá,\n\n"
        "O teu registo foi confirmado com sucesso.\n"
        "Já podes fazer login e aceder à tua área de utilizador.\n\n"
        "Obrigado!"
    )

    html_content = """
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 640px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);">
          <h2 style="color:#222; margin-top: 0;">Registo confirmado</h2>
          <p style="color:#444; line-height: 1.5;">
            O teu registo foi confirmado com sucesso. Já podes entrar e aceder à tua área de utilizador.
          </p>
          <p style="color:#666; line-height: 1.5; margin-bottom: 0;">Obrigado!</p>
        </div>

        <p style="text-align:center; color:#999; font-size: 12px; margin-top: 14px;">
          Extreme Way
        </p>
      </body>
    </html>
    """

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()