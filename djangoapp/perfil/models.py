from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.forms import ValidationError
from utils.model_validators import validar_nif


class Perfil(models.Model):
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        verbose_name="Usuário",
    )
    data_nascimento = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    telemovel = models.CharField(
        max_length=9,
        blank=True,
        verbose_name="Telemóvel",
    )
    nif = models.CharField(max_length=9, blank=True)

    def clean(self):
        error_messages = {}

        if not self.data_nascimento:
            error_messages['data_nascimento'] = 'Data de Nascimento \
            é obrigatória.'

        if not self.telemovel:
            error_messages['telemovel'] = 'Telemóvel é obrigatório.'

        if self.nif and not validar_nif(self.nif):
            error_messages['nif'] = 'NIF inválido.'

        raise ValidationError(error_messages)

    def __str__(self):
        return f'{self.usuario.first_name} {self.usuario.last_name}'


class Morada(models.Model):
    class Meta:
        verbose_name = "Morada"
        verbose_name_plural = "Moradas"

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
    )
    finalidade_morada = models.CharField(blank=False, choices=(
        ('E', 'Entrega'),
        ('F', 'Faturação')
    )
    )
    morada = models.CharField(max_length=100, blank=True)
    numero = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Número",)
    codigo_postal = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="Código Postal",)
    ext_codigo_postal = models.CharField(
        max_length=3,
        blank=True,
        verbose_name="Extensão Código Postal",)

    def __str__(self):
        return self.finalidade_morada
