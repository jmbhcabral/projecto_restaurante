''' Este ficheiro contém os modelos de dados da aplicação fidelidade '''

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from restau.models import Products, Ementa
from utils.model_validators import calcular_pontos


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

        self.pontos_recompensa, self.pontos_para_oferta = calcular_pontos(
            self.produto, self.fidelidade)

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

    compra = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        verbose_name='Compra',
    )

    pontos_adicionados = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        verbose_name='Pontos Adicionados',
    )

    criado_em = models.DateTimeField(
        default=timezone.now,
        verbose_name='Criado em',)

    chave_g = models.CharField(
        max_length=200,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Chave G',
    )

    expirado = models.BooleanField(
        verbose_name='Expirado',
        default=False,
    )

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
        verbose_name='Pontos Gastos',
    )
    processado = models.BooleanField(
        verbose_name='Processado',
        default=False,
    )

    criado_em = models.DateTimeField(
        default=timezone.now,
        verbose_name='Criado em',
    )

    def __str__(self):
        return f" {self.fidelidade} - {self.utilizador} "


class Perguntas(models.Model):
    class Meta:
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'

    pergunta = models.CharField(max_length=200, verbose_name='Pergunta')

    def __str__(self):
        return self.pergunta


class Respostas(models.Model):
    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'

    pergunta = models.ForeignKey(
        Perguntas,
        on_delete=models.CASCADE,
        verbose_name='Pergunta',
    )

    resposta = models.CharField(max_length=200, verbose_name='Resposta')

    def __str__(self):
        return self.resposta


class RespostaFidelidade(models.Model):
    class Meta:
        verbose_name = 'Resposta Fidelidade'
        verbose_name_plural = 'Respostas Fidelidade'

    resposta = models.ForeignKey(
        Respostas,
        on_delete=models.CASCADE,
        verbose_name='Resposta',
    )

    tipo_fidelidade = models.ForeignKey(
        Fidelidade,
        on_delete=models.CASCADE,
        verbose_name='Tipo Fidelidade',
    )

    def __str__(self):
        return f"{self.resposta}"
