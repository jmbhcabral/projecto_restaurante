''' Este módulo contém os modelos de dados para o aplicativo de perfil. '''
# djangoapp/perfil/models.py
from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models import Q
from django.forms import ValidationError
from django.utils import timezone

from djangoapp.fidelidade.models import Fidelidade, RespostaFidelidade
from djangoapp.utils.model_validators import validar_nif

User = settings.AUTH_USER_MODEL

class Perfil(models.Model):
    """Perfil do utilizador (dados reais do negócio)."""
    class Meta:
        """Meta class for the Perfil model."""
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

        indexes = [
            models.Index(fields=["numero_cliente"]),
            models.Index(fields=["telemovel"]),
        ]

        constraints = [
            # English comment: unique phone only when not empty
            models.UniqueConstraint(
                fields=["telemovel"],
                condition=~Q(telemovel=""),
                name="uniq_perfil_telemovel_non_empty",
            )
        ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Utilizador",
    )

    # Dados pessoais (não obrigatórios no registo)
    data_nascimento = models.DateField(null=True, blank=True)
    telemovel = models.CharField(max_length=9, blank=True, verbose_name="Telemóvel")
    nif = models.CharField(max_length=9, blank=True)

    # Negócio
    numero_cliente = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        verbose_name="Número Cliente",
        db_index=True,
    )

    estudante = models.ForeignKey(
        RespostaFidelidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Estudante",
    )

    tipo_fidelidade = models.ForeignKey(
        Fidelidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo Fidelidade",
    )

    qr_code = models.ImageField(upload_to="assets/qrcodes/", blank=True, null=True)

    # Onboarding (novo) — NÃO mexe no first_login do RN
    onboarding_optional_completed = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    onboarding_required_completed = models.BooleanField(default=False)

    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    # Capacidades (não-linear)
    has_valid_nif = models.BooleanField(default=False)
    has_delivery_address = models.BooleanField(default=False)
    has_billing_address = models.BooleanField(default=False)

    ultima_atualizacao_data_nascimento = models.DateTimeField(
        null=True, blank=True)

    ultima_actividade = models.DateTimeField(
        default=timezone.now,
        verbose_name="Última Actividade",
        blank=True,
        null=True,
    )
    reset_password_code = models.IntegerField(
        verbose_name="Código de Reset de Password",
        blank=True,
        null=True,
        default=000000000
    )

    reset_password_code_str = models.CharField(
        verbose_name="Código de Reset de Password",
        blank=True,
        null=True,
        max_length=6,
    )

    reset_password_code_expires = models.DateTimeField(
        verbose_name="Expiração do Código de Reset de Password",
        blank=True,
        null=True,
        default=timezone.now
    )
    data_cancelamento = models.DateTimeField(
        verbose_name="Data de Cancelamento",
        blank=True,
        null=True,
    )
    notificacoes_email = models.BooleanField(
        verbose_name="Notificações por Email",
        default=True,
    )
    notificacoes_telemovel = models.BooleanField(
        verbose_name="Notificações por Telemóvel",
        default=True,
    )
    first_login = models.BooleanField(
        verbose_name="Primeiro Login",
        default=True,
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        error_messages = {}

        if self.nif and not validar_nif(self.nif):
            error_messages['nif'] = 'NIF inválido.'

        if self.telemovel:
            t = self.telemovel.strip()
            if len(t) != 9 or not t.isdigit():
                error_messages['telemovel'] = "O telemóvel tem de ter 9 dígitos."

        if error_messages:
            raise ValidationError(error_messages)

    def __str__(self):
        return f'{self.usuario.first_name} {self.usuario.last_name}'


class PendingSignup(models.Model):
    """
    Temporary signup payload until code verification.
    Stores password as a Django-compatible hash (never plaintext).
    """

    class Meta:
        verbose_name = "Pending Signup"
        verbose_name_plural = "Pending Signups"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["used_at"]),
        ]

    email = models.EmailField(unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)

    used_at = models.DateTimeField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    def set_temp_password(self, raw_password: str) -> None:
        # English comment: store as Django password hash; can later be assigned to User.password directly.
        self.password_hash = make_password(raw_password)

    def mark_used(self) -> None:
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])


class VerificationCode(models.Model):
    """
    Stores verification codes for multiple purposes (signup, email change, etc.)
    Code is stored as a digest (never store the raw code).
    """

    class Meta:
        verbose_name = "Verification Code"
        verbose_name_plural = "Verification Codes"
        indexes = [
            models.Index(fields=["email", "purpose"]),
            models.Index(fields=["purpose", "expires_at"]),
            models.Index(fields=["created_at"]),

            # cleanup speed (expired + used)
            models.Index(fields=["expires_at"]),
            models.Index(fields=["used_at"]),
        ]

    email = models.EmailField(db_index=True)
    purpose = models.CharField(max_length=64, db_index=True)

    # store only a digest (HMAC/sha256), never the raw code
    code_digest = models.CharField(max_length=128)

    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)

    # attempts/resends are useful for security + audit
    attempts = models.PositiveSmallIntegerField(default=0)
    resend_count = models.PositiveSmallIntegerField(default=0)

    # Optional audit context (safe enough)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

class Morada(models.Model):
    """Moradas do utilizador (Entrega / Faturação)."""

    class Meta:
        verbose_name = "Morada"
        verbose_name_plural = "Moradas"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "purpose"],
                name="uniq_address_per_user_purpose",
            )
        ]

    class Purpose(models.TextChoices):
        DELIVERY = "delivery", "Entrega"
        BILLING = "billing", "Faturação"

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="moradas",
        verbose_name="Utilizador",
    )

    purpose = models.CharField(max_length=20, choices=Purpose.choices)

    morada = models.CharField(max_length=120)
    numero = models.CharField(max_length=10)
    codigo_postal = models.CharField(max_length=4)
    ext_codigo_postal = models.CharField(max_length=3)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        errors: dict[str, str] = {}

        if not self.morada:
            errors["morada"] = "Morada é obrigatória."
        if not self.numero:
            errors["numero"] = "Número é obrigatório."
        if not self.codigo_postal:
            errors["codigo_postal"] = "Código Postal é obrigatório."
        if not self.ext_codigo_postal:
            errors["ext_codigo_postal"] = "Extensão do Código Postal é obrigatória."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.usuario_id} - {self.purpose}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)  # Expira em 15 minutos

    def __str__(self):
        return f"Reset Token for {self.user.email}"
    
    
class PushNotificationToken(models.Model):
    '''Model for the push notification token.'''
    class Meta:
        verbose_name = "Token de Notificação Push"
        verbose_name_plural = "Tokens de Notificação Push"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expo_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expo_token}"


class Notification(models.Model):
    """Regista as notificações enviadas a utilizadores específicos."""

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ("-created_at",)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Utilizador",
    )
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def mark_as_read(self):
        """Atualiza o registo para indicar que a notificação foi lida."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])

    def __str__(self):
        return f"{self.user.username} - {self.title or 'Sem título'}"
    
