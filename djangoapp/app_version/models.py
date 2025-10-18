from django.core.exceptions import ValidationError
from django.db import models


class AppVersion(models.Model):
    SISTEMA_OPERATIVO_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
    )

    sistema_operativo = models.CharField(
        max_length=10,
        choices=SISTEMA_OPERATIVO_CHOICES,
        db_index=True,
    )
    versao = models.CharField(max_length=20)
    forcar_update = models.BooleanField(default=False)

    # Sugestão: DateTime para ordenação/“latest” mais precisa
    # Se quiseres manter DateField, podes, mas DateTimeField é mais robusto.
    data_lancamento = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-data_lancamento']
        # Fonte de verdade: não podem existir duplicados do par (SO, versão)
        constraints = [
            models.UniqueConstraint(
                fields=['sistema_operativo', 'versao'],
                name='unique_appversion_os_version',
            ),
        ]
        # Opcional: permite usar .latest() sem teres de passar o campo
        get_latest_by = 'data_lancamento'

    def __str__(self):
        return f'{self.sistema_operativo.upper()} - v{self.versao}'

    def clean(self):
        # 1) Duplicados (corrigido): mesmo SO + mesma versão, excluindo o próprio
        dup = AppVersion.objects.filter(
            sistema_operativo=self.sistema_operativo,
            versao=self.versao,
        ).exclude(pk=self.pk).exists()
        if dup:
            raise ValidationError('Já existe esta versão para este sistema operativo.')

        # 2) (Opcional) Permitir apenas UM “forçar update” por SO
        if self.forcar_update:
            ja_forcadas = AppVersion.objects.filter(
                sistema_operativo=self.sistema_operativo,
                forcar_update=True,
            ).exclude(pk=self.pk).exists()
            if ja_forcadas:
                raise ValidationError(
                    'Já existe uma versão marcada como atualização obrigatória para este sistema operativo.'
                )