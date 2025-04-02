from django.db import models


class AppVersion(models.Model):
    SISTEMA_OPERATIVO_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
    )

    sistema_operativo = models.CharField(max_length=10, choices=SISTEMA_OPERATIVO_CHOICES)
    versao = models.CharField(max_length=20)
    forcar_update = models.BooleanField(default=False)
    data_lancamento = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.sistema_operativo.upper()} - v{self.versao}"
