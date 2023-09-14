from django.db import models
from utils.model_validators import positive_price
from utils.images import resize_image
from decimal import Decimal


class Category(models.Model):
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    nome = models.CharField(max_length=200, null=False,
                            default='nova_categoria',)
    ordem = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


class SubCategory(models.Model):
    class Meta:
        verbose_name = 'Subcategoria'
        verbose_name_plural = 'Subcategorias'

    nome = models.CharField(max_length=200, null=False,
                            default='nova_subcategoria',)
    categoria = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None
    )
    ordem = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


class Percentage(models.Model):
    class Meta:
        verbose_name = 'Percentagem'
        verbose_name_plural = 'Percentagens'

    valor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Percentagem de desconto (de 0 a 100)',
        default=0.0  # type: ignore
    )

    def __str__(self):
        return str(self.valor)


class FrontendSetup(models.Model):
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome',
        help_text='Nome da configuração'
    )
    imagem_logo = models.ImageField(
        upload_to='assets/frontend/logo',
        blank=True,
        null=True,
        verbose_name='Logo',
        default='',
        # validators=[validate_png]
    )

    imagem_topo = models.ImageField(
        upload_to='assets/frontend/',
        blank=True,
        null=True,
        verbose_name='Imagem',
        default='',
        # validators=[validate_png]
    )

    imagem_padrao = models.ImageField(
        upload_to='assets/Products/default/',
        blank=True,
        null=True,
        default='default_image.jpg',
        verbose_name='Imagem Padrão',
        # validators=[validate_png]
    )

    def save(self, *args, **kwargs):
        current_imagem_logo_name = str(self.imagem_logo.name)
        current_imagem_topo_name = str(self.imagem_topo.name)
        current_imagem_padrao_name = str(self.imagem_padrao.name)
        super().save(*args, **kwargs)
        imagem_logo_changed = False
        imagem_topo_changed = False
        imagem_padrao_changed = False

        if self.imagem_logo:
            imagem_logo_changed = current_imagem_logo_name != \
                self.imagem_logo.name

        if self.imagem_topo:
            imagem_topo_changed = current_imagem_topo_name != \
                self.imagem_topo.name

        if self.imagem_padrao:
            imagem_padrao_changed = current_imagem_padrao_name != \
                self.imagem_padrao.name

        if imagem_logo_changed:
            print('Resizing logo')
            resize_image(self.imagem_logo, 200)

        if imagem_topo_changed:
            print('Resizing imagem de topo')
            # Substitua 200 pelo tamanho desejado
            resize_image(self.imagem_topo, 900)

        if imagem_padrao_changed:
            print('resizing')
            resize_image(self.imagem_padrao, 500)

    def __str__(self):
        return self.nome


class Products(models.Model):
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    nome = models.CharField(
        max_length=200,
        verbose_name='Produto'
    )

    descricao_curta = models.CharField(
        max_length=200,
        verbose_name='Descrição Curta',
    )

    descricao_longa = models.TextField(
        verbose_name='Descrição Longa',
        blank=True,
        null=True,
        default=None,
    )

    preco_1 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[positive_price],
        verbose_name='Preço 1',
        blank=True,
        null=True,
        default=Decimal('0.00'),
    )

    preco_2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[positive_price],
        verbose_name='Preço 2',
        blank=True,
        null=True,
        default=Decimal('0.00'),
    )

    preco_3 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[positive_price],
        verbose_name='Preço 3',
        blank=True,
        null=True,
        default=Decimal('0.00'),
    )

    preco_4 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[positive_price],
        verbose_name='Preço 4',
        blank=True,
        null=True,
        default=Decimal('0.00'),
    )

    preco_5 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[positive_price],
        verbose_name='Preço 5',
        blank=True,
        null=True,
        default=Decimal('0.00'),
    )

    preco_6 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[positive_price],
        verbose_name='Preço 6',
        blank=True,
        null=True,
        default=Decimal('0.00'),
    )

    preco_promo = models.FloatField(
        default=0.00,
        validators=[positive_price],
        verbose_name='Preço Promocional',
    )

    percentagem_desconto = models.ForeignKey(
        Percentage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    categoria = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )

    subcategoria = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )

    ordem = models.IntegerField(default=0)

    visibilidade = models.BooleanField(default=True)

    imagem = models.ImageField(
        upload_to='assets/Products/',
        blank=True,
        null=True,
        default='',
        verbose_name='Imagem',
        # validators=[validate_png]
    )

    def save(self, *args, **kwargs):
        current_imagem_name = str(self.imagem.name)
        super().save(*args, **kwargs)
        imagem_changed = False

        if self.imagem:
            imagem_changed = current_imagem_name != self.imagem.name

        if imagem_changed:
            print('resizing')
            resize_image(self.imagem, 500)

    def __str__(self):
        return self.nome


class Ementa(models.Model):
    class Meta:
        verbose_name = 'Ementa'
        verbose_name_plural = 'Ementas'

    nome = models.CharField(
        max_length=200,
        verbose_name='Ementa'
    )

    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição',
    )

    nome_campo_preco_selecionado = models.CharField(
        max_length=10,
        choices=[
            ('preco_1', 'Preço 1'),
            ('preco_2', 'Preço 2'),
            ('preco_3', 'Preço 3'),
            ('preco_4', 'Preço 4'),
            ('preco_5', 'Preço 5'),
            ('preco_6', 'Preço 6'),
        ],
        verbose_name='Preço',
    )

    produtos = models.ManyToManyField(Products)

    def __str__(self):
        return self.nome


class ProdutosEmenta(models.Model):
    class Meta:
        verbose_name = 'Produto Ementa'
        verbose_name_plural = 'Produtos Ementas'

    ementa = models.ForeignKey(
        Ementa,
        on_delete=models.CASCADE,
        verbose_name='Ementa',
        related_name='ementas',
    )

    produto = models.ManyToManyField(
        Products,
        verbose_name='Produto',
        related_name='produtos',
    )

    def __str__(self):
        return self.ementa.nome


class Fidelizacao(models.Model):
    class Meta:
        verbose_name = 'Fidelização'
        verbose_name_plural = 'Fidelizações'

    nome = models.CharField(max_length=200, verbose_name='Nome')
    unidade = models.FloatField(default=0.00, verbose_name='Unidade para Euro')

    def __str__(self):
        return self.nome


class ProdutosFidelizacao(models.Model):
    class Meta:
        verbose_name = 'Produto Fidelização'
        verbose_name_plural = 'Produtos Fidelizações'

    fidelizacao = models.ForeignKey(
        Fidelizacao,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )

    produto_fidelizacao = models.OneToOneField(
        Products,
        unique=True,
        on_delete=models.SET_NULL,
        related_name='produto_fidelizacao',
        blank=True,
        null=True,
        default=None,
    )
    pontos_recompensa = models.ForeignKey(
        Products,
        on_delete=models.SET_NULL,
        related_name='pontos_recompensa',
        blank=True,
        null=True,
        default=None,
    )
    pontos_para_oferta = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.produto_fidelizacao)
