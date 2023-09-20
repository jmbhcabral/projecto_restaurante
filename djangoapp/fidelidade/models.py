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
    class Meta:
        verbose_name = 'Produto Fidelidade Individual'
        verbose_name_plural = 'Produtos Fidelidade Individual'

    fidelidade = models.ForeignKey(Fidelidade, on_delete=models.CASCADE)
    produto = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name='Produto',
    )

    pontos_recompensa = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Pontos Recompensa',
    )
    pontos_para_oferta = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Pontos para Oferta',
    )

    def __str__(self):
        return f" {self.fidelidade} "
