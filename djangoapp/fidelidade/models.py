from django.db import models
from restau.models import Products, Ementa
from django.core.exceptions import ValidationError


class Fidelidade(models.Model):
    class Meta:
        verbose_name = 'Fidelidade'
        verbose_name_plural = 'Fidelidades'

    nome = models.CharField(max_length=200, verbose_name='Nome')
    unidade = models.FloatField(default=0.00, verbose_name='Unidade por Euro')
    ementa = models.ForeignKey(
        Ementa,
        on_delete=models.CASCADE,
        default=None,
    )

    def __str__(self):
        return self.nome


class ProdutoFidelidadeIndividual(models.Model):
    produto = models.ForeignKey(Products, on_delete=models.CASCADE)
    fidelidade = models.ForeignKey(Fidelidade, on_delete=models.CASCADE)
    ementa = models.ForeignKey(
        Ementa, on_delete=models.CASCADE, related_name='produtos_fidelidade')
    pontos_recompensa = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Pontos Recompensa',
    )
    pontos_para_oferta = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Pontos para Oferta',
    )

    def save(self, *args, **kwargs):
        if self.fidelidade.ementa is None:
            raise ValidationError("A fidelidade deve ter uma ementa associada.")
        # Certifique-se de que o produto está na ementa associada à fidelidade
        if self.produto not in self.fidelidade.ementa.produtos.all():
            raise ValidationError(
                "O produto deve pertencer à ementa da fidelidade.")
        super(ProdutoFidelidadeIndividual, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.produto} - {self.fidelidade} - "\
               f"{self.pontos_recompensa} pontos - "\
               f"{self.pontos_para_oferta} pontos para oferta"
