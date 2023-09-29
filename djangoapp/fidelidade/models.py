from django.db import models
from restau.models import Products, Ementa
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Fidelidade(models.Model):
    class Meta:
        verbose_name = 'Fidelidade'
        verbose_name_plural = 'Fidelidades'

    nome = models.CharField(max_length=200, verbose_name='Nome')
    desconto = models.IntegerField(
        null=False, blank=False, verbose_name='Desconto')
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

    pontos_recompensa = models.IntegerField(
        null=False, blank=False,
        verbose_name='Pontos Recompensa',
    )
    pontos_para_oferta = models.IntegerField(
        null=False, blank=False,
        verbose_name='Pontos para Oferta',
    )
    visibilidade = models.BooleanField(
        verbose_name='Visibilidade',
        default=False,
    )

    def save(self, *args, **kwargs):
        ementa = self.fidelidade.ementa
        preco_field = ementa.nome_campo_preco_selecionado
        preco = getattr(self.produto, preco_field)
        preco_int = int(preco * 100)
        # if preco is not None:
        #     preco_int = int(preco * 100)
        # else:
        #     raise ValidationError(
        #         'Algum produto não tem um preço definido')

        desconto = self.fidelidade.desconto
        pontos_necessarios = int(preco_int / (desconto / 100))

        self.pontos_recompensa = preco_int
        self.pontos_para_oferta = pontos_necessarios

        super().save(*args, **kwargs)

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

    def __str__(self):
        return f" {self.fidelidade} - {self.utilizador} "
