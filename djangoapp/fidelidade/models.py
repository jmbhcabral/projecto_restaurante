from django.db import models
from restau.models import Products, Ementa
from django.contrib.auth.models import User


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


class ComprasFidelidade(models.Model):
    class Meta:
        verbose_name = 'Compra Fidelidade'
        verbose_name_plural = 'Compras Fidelidade'

    fidelidade = models.ForeignKey(
        Fidelidade,
        on_delete=models.CASCADE)

    utilizador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    pontos_adicionados = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Pontos Adicionados',
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.fidelidade} - {self.utilizador} "


class OfertasFidelidade(models.Model):
    class Meta:
        verbose_name = 'Oferta Fidelidade'
        verbose_name_plural = 'Ofertas Fidelidade'

    fidelidade = models.ForeignKey(
        Fidelidade,
        on_delete=models.CASCADE)

    utilizador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    pontos_gastos = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='Pontos Adicionados',
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    # def clean(self):
    #     total_pontos_adicionados = ComprasFidelidade.objects.filter(
    #         utilizador=self.utilizador) \
    #         .aggregate(Sum('pontos_adicionados'))['pontos_adicionados__sum'] or 0

    #     total_pontos_gastos = OfertasFidelidade.objects.filter(
    #         utilizador=self.utilizador) \
    #         .aggregate(Sum('pontos_gastos'))['pontos_gastos__sum'] or 0

    #     if self.pontos_gastos:
    #         total_pontos_gastos += self.pontos_gastos

    #     if total_pontos_gastos > total_pontos_adicionados:
    #         raise ValidationError(
    #             f'O {self.utilizador} tem pontos suficientes para realizar esta oferta.'
    #         )

    def __str__(self):
        return f" {self.fidelidade} - {self.utilizador} "
