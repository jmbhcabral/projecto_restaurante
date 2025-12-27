''' Este ficheiro contém os modelos de dados da aplicação fidelidade '''

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from djangoapp.restau.models import Ementa, Products
from djangoapp.utils.model_validators import calcular_pontos


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
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
    )

    compra = models.DecimalField(
        max_digits=10, decimal_places=3, null=False, blank=False,
        verbose_name='Compra',
    )

    pontos_adicionados = models.DecimalField(
        max_digits=10, decimal_places=3, null=False, blank=False,
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
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
    )

    pontos_gastos = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False,
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
    

class MovimentoPontos(models.Model):
    class Tipo(models.TextChoices):
        CREDITO = "CREDITO", "Crédito"          # compras, bónus
        DEBITO_RES = "DEBITO_RES", "Resgate"    # oferta / consumo
        DEBITO_EXP = "DEBITO_EXP", "Expiração"  # expiração por inatividade
        AJUSTE = "AJUSTE", "Ajuste"             # correções manuais

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        CONFIRMADO = "CONFIRMADO", "Confirmado"
        CANCELADO = "CANCELADO", "Cancelado"

    utilizador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="movimentos_pontos",
    )

    fidelidade = models.ForeignKey(
        "Fidelidade",
        on_delete=models.CASCADE,
        related_name="movimentos_pontos",
    )

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMADO,
    )

    # pontos POSITIVOS; o sinal é dado pelo tipo (crédito vs débito)
    pontos = models.DecimalField(
        max_digits=10,
        decimal_places=3,
    )

    # ligações aos registos antigos (opcional mas muito útil para auditoria)
    compra = models.ForeignKey(
        "ComprasFidelidade",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="movimentos_pontos",
    )

    oferta = models.ForeignKey(
        "OfertasFidelidade",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="movimentos_pontos",
    )

    criado_em = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        verbose_name = "Movimento de Pontos"
        verbose_name_plural = "Movimentos de Pontos"
        indexes = [
            models.Index(fields=["utilizador", "fidelidade", "status"]),
            models.Index(fields=["utilizador", "criado_em"]),
            models.Index(fields=["tipo"]),
        ]

    def __str__(self):
        return f"{self.utilizador} - {self.tipo} - {self.pontos}"


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


class NotificacaoAutomatica(models.Model):
    TIPO_CHOICES = [
        ('birthday_minus_8', 'Aniversário -8 dias'),
        ('birthday_day', 'Aniversário - dia'),
        ('points_minus_15', 'Pontos -15 dias'),
        ('points_minus_7', 'Pontos -7 dia'),
        ('points_minus_1', 'Pontos -1 dia'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)
    
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
    )

    referencia_data = models.DateField()
    enviado_em = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ('user', 'tipo', 'referencia_data')
        # garante que não mandas 2x a mesma notificação para o mesmo user / mesmo evento