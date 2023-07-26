from django.db import models
from utils.model_validators import positive_price
from utils.images import resize_image


class Category(models.Model):
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    categoria = models.CharField(max_length=200)

    def __str__(self):
        return self.categoria


class SubCategory(models.Model):
    class Meta:
        verbose_name = 'Subcategoria'
        verbose_name_plural = 'Subcategorias'

    subcategoria = models.CharField(max_length=200)

    def __str__(self):
        return self.subcategoria


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
    )
    preco = models.FloatField(
        default=0.00,
        validators=[positive_price],
        verbose_name='Preço',
    )
    preco_promo = models.FloatField(
        default=0.00,
        validators=[positive_price],
        verbose_name='Preço Promocional',
    )
    percentagem_desconto = models.ForeignKey(
        Percentage,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    categoria = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )
    subcategoria = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    visibilidade = models.BooleanField(default=True)

    imagem = models.ImageField(
        upload_to='assets/Products/',
        blank=True,
        null=True,
        default='default_image.jpg',
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
            resize_image(self.imagem, 500)

    def __str__(self):
        return self.nome
