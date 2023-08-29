from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE)
    data_nascimento = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    telemovel = models.CharField(max_length=9, blank=True)
    nif = models.CharField(max_length=9, blank=True)

    def __str__(self):
        return f'{self.usuario.first_name} {self.usuario.last_name}'


class Morada(models.Model):
    class Meta:
        verbose_name = "Morada"
        verbose_name_plural = "Moradas"

    usuario = models.OneToOneField(
        Perfil, on_delete=models.CASCADE)
    finalidade_morada = models.CharField(blank=False, choices=(
        ('E', 'Entrega'),
        ('F', 'Faturação')
    )
    )
    morada = models.CharField(max_length=100, blank=True)
    numero = models.CharField(max_length=10, blank=True)
    codigo_postal = models.CharField(max_length=4, blank=True)
    ext_codigo_postal = models.CharField(max_length=3, blank=True)

    def __str__(self):
        return self.finalidade_morada
