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


class Fotos(models.Model):
    class Meta:
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'

    imagem = models.ImageField(
        upload_to='assets/frontend/galeria',
        blank=True,
        null=True,
        verbose_name='Imagem',
        default='',
    )

    is_visible = models.BooleanField(
        default=True,
        verbose_name='Visibilidade',
        help_text='Visibilidade da foto'
    )

    ordem = models.IntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem da foto na galeria',
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):

        current_imagem_name = str(self.imagem.name)
        super().save(*args, **kwargs)
        imagem_changed = False

        if self.imagem:
            imagem_changed = current_imagem_name != self.imagem.name

        if imagem_changed:
            print('resizing')
            resize_image(self.imagem, 300)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.imagem.name


class ImagemLogo(models.Model):
    class Meta:
        verbose_name = 'Imagem Logo'
        verbose_name_plural = 'Imagens Logo'

    imagem = models.ImageField(
        upload_to='assets/frontend/imagem_logo',
        blank=True,
        null=True,
        verbose_name='Imagem do logo',
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade do logo.'
    )

    def save(self, *args, **kwargs):

        current_imagem_name = str(self.imagem.name)
        super().save(*args, **kwargs)
        imagem_changed = False

        if self.imagem:
            imagem_changed = current_imagem_name != self.imagem.name

        if imagem_changed:
            print('resizing')
            resize_image(self.imagem, 200)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.imagem.name


class ImagemTopo(models.Model):
    class Meta:
        verbose_name = 'Imagem Topo'
        verbose_name_plural = 'Imagens Topo'

    imagem = models.ImageField(
        upload_to='assets/frontend/imagem_topo',
        blank=True,
        null=True,
        verbose_name='Imagem Topo',
        default='',
    )

    is_visible = models.BooleanField(
        default=True,
        verbose_name='Visibilidade',
        help_text='Visibilidade da imagem.'
    )

    def save(self, *args, **kwargs):

        current_imagem_name = str(self.imagem.name)
        super().save(*args, **kwargs)
        imagem_changed = False

        if self.imagem:
            imagem_changed = current_imagem_name != self.imagem.name

        if imagem_changed:
            print('resizing')
            resize_image(self.imagem, 900)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.imagem.name


class Intro(models.Model):
    class Meta:
        verbose_name = 'Intro'
        verbose_name_plural = 'Intros'

    texto = models.TextField(
        max_length=1500,
        verbose_name='Texto da intro',
        blank=True,
        null=True,
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da intro.'
    )

    def __str__(self):
        return self.texto


class IntroImagem(models.Model):
    class Meta:
        verbose_name = 'Intro Imagem'
        verbose_name_plural = 'Intros Imagens'

    imagem = models.ImageField(
        upload_to='assets/frontend/intro_imagem',
        blank=True,
        null=True,
        verbose_name='Imagem da intro',
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da imagem.'
    )

    def save(self, *args, **kwargs):

        current_imagem_name = str(self.imagem.name)
        super().save(*args, **kwargs)
        imagem_changed = False

        if self.imagem:
            imagem_changed = current_imagem_name != self.imagem.name

        if imagem_changed:
            print('resizing')
            resize_image(self.imagem, 1200)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.imagem.name


class FraseInspiradora(models.Model):
    class Meta:
        verbose_name = 'Frase Inspiradora'
        verbose_name_plural = 'Frases Inspiradoras'

    texto = models.TextField(
        max_length=250,
        verbose_name='Frase Inspiradora',
        blank=True,
        null=True,
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da frase inspiradora.'
    )

    def __str__(self):
        return self.texto


class FraseCima(models.Model):
    class Meta:
        verbose_name = 'Frase Cima'
        verbose_name_plural = 'Frases Cima'

    texto = models.TextField(
        max_length=250,
        verbose_name='Frase Cima',
        blank=True,
        null=True,
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da frase cima.'
    )

    def __str__(self):
        return self.texto


class ImagemFraseCima(models.Model):
    class Meta:
        verbose_name = 'Imagem Frase Cima'
        verbose_name_plural = 'Imagens Frases Cima'

    imagem = models.ImageField(
        upload_to='assets/frontend/imagem_frase_cima',
        blank=True,
        null=True,
        verbose_name='Imagem Frase Cima',
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da imagem.'
    )

    def save(self, *args, **kwargs):

        current_imagem_name = str(self.imagem.name)
        super().save(*args, **kwargs)
        imagem_changed = False

        if self.imagem:
            imagem_changed = current_imagem_name != self.imagem.name

        if imagem_changed:
            print('resizing')
            resize_image(self.imagem, 300)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.imagem.name


class FraseBaixo(models.Model):
    class Meta:
        verbose_name = 'Frase Baixo'
        verbose_name_plural = 'Frases Baixo'

    texto = models.TextField(
        max_length=250,
        verbose_name='Frase Baixo',
        blank=True,
        null=True,
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da frase baixo.'
    )

    def __str__(self):
        return self.texto


class ImagemFraseBaixo(models.Model):
    class Meta:
        verbose_name = 'Imagem Frase Baixo'
        verbose_name_plural = 'Imagens Frases Baixo'

    imagem = models.ImageField(
        upload_to='assets/frontend/imagem_frase_baixo',
        blank=True,
        null=True,
        verbose_name='Imagem Frase Baixo',
        default='',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da imagem.'
    )

    def save(self, *args, **kwargs):

        current_imagem_name = str(self.imagem.name)
        super().save(*args, **kwargs)
        imagem_changed = False

        if self.imagem:
            imagem_changed = current_imagem_name != self.imagem.name

        if imagem_changed:
            print('resizing')
            resize_image(self.imagem, 300)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.imagem.name


class ImagemPadrao(models.Model):
    class Meta:
        verbose_name = 'Imagem Padrão'
        verbose_name_plural = 'Imagens Padrão'

    imagem = models.ImageField(
        upload_to='assets/frontend/imagem_padrao',
        blank=True,
        null=True,
        default='default_image.jpg',
        verbose_name='Imagem Padrão',
    )

    is_visible = models.BooleanField(
        default=False,
        verbose_name='Visibilidade',
        help_text='Visibilidade da imagem.'
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
            super().save(*args, **kwargs)

    def __str__(self):
        return self.imagem.name


class ContactosSite(models.Model):
    class Meta:
        verbose_name = 'Contacto Site'
        verbose_name_plural = 'Contactos Site'

    morada = models.TextField(
        max_length=250,
        verbose_name='Morada',
        blank=True,
        null=True,
        default='',
    )

    telefone = models.CharField(
        max_length=15,
        verbose_name='Telefone',
        blank=True,
        null=True,
        default='',
    )

    email = models.CharField(
        max_length=50,
        verbose_name='Email',
        blank=True,
        null=True,
        default='',
    )

    facebook = models.CharField(
        max_length=250,
        verbose_name='Facebook',
        blank=True,
        null=True,
        default='',
    )

    facebook_icon = models.CharField(
        max_length=250,
        verbose_name='Facebook Icon',
        blank=True,
        null=True,
        default='',
    )

    instagram = models.CharField(
        max_length=250,
        verbose_name='Instagram',
        blank=True,
        null=True,
        default='',
    )

    instagram_icon = models.CharField(
        max_length=250,
        verbose_name='Instagram Icon',
        blank=True,
        null=True,
        default='',
    )

    def __str__(self):
        return self.morada


class GoogleMaps(models.Model):
    class Meta:
        verbose_name = 'Google Maps'
        verbose_name_plural = 'Google Maps'

    iframe = models.TextField(
        max_length=500,
        verbose_name='Iframe',
        blank=True,
        null=True,
        default='',
    )

    def __str__(self):
        return self.iframe


class Horario(models.Model):
    class Meta:
        verbose_name = 'Horário'
        verbose_name_plural = 'Horários'

    DIA_SEMANA_CHOICES = [
        ('Segunda', 'Segunda-feira'),
        ('Terça', 'Terça-feira'),
        ('Quarta', 'Quarta-feira'),
        ('Quinta', 'Quinta-feira'),
        ('Sexta', 'Sexta-feira'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
        ('Feriados', 'Feriados')
    ]

    STATUS_CHOICES = [
        ('Aberto', 'Aberto'),
        ('Encerrado', 'Encerrado'),
    ]

    dia_semana = models.CharField(
        max_length=10,
        choices=DIA_SEMANA_CHOICES,
        verbose_name='Dia da semana',
        blank=True,
        null=True,
        default='',
    )

    hora_abertura_almoco = models.TimeField(
        verbose_name='Hora de abertura do almoço',
        blank=True,
        null=True,
    )

    hora_fecho_almoco = models.TimeField(
        verbose_name='Hora de fecho do almoço',
        blank=True,
        null=True,
    )

    hora_abertura_jantar = models.TimeField(
        verbose_name='Hora de abertura do jantar',
        blank=True,
        null=True,
    )

    hora_fecho_jantar = models.TimeField(
        verbose_name='Hora de fecho do jantar',
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='Status',
        blank=True,
        null=True,
        default='Aberto',
    )

    def __str__(self):
        return f'{self.dia_semana}: {self.hora_abertura_almoco} - ' \
               f'{self.hora_fecho_almoco} | {self.hora_abertura_jantar} - ' \
               f'{self.hora_fecho_jantar}'


class ActiveSetup(models.Model):
    active_imagem_logo = models.ForeignKey(
        'ImagemLogo',
        related_name='active_imagem_logo_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_imagem_topo = models.ForeignKey(
        'ImagemTopo',
        related_name='active_imagem_topo_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_intro = models.ForeignKey(
        'Intro',
        related_name='active_intro_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_intro_imagem = models.ForeignKey(
        'IntroImagem',
        related_name='active_intro_imagem_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_frase_inspiradora = models.ForeignKey(
        'FraseInspiradora',
        related_name='active_frase_inspiradora_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_ementa = models.ForeignKey(
        'Ementa',
        related_name='active_ementa_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_frase_cima = models.ForeignKey(
        'FraseCima',
        related_name='active_frase_cima_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_imagem_frase_cima = models.ForeignKey(
        'ImagemFraseCima',
        related_name='active_imagem_frase_cima_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_frase_baixo = models.ForeignKey(
        'FraseBaixo',
        related_name='active_frase_baixo_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_imagem_frase_baixo = models.ForeignKey(
        'ImagemFraseBaixo',
        related_name='active_imagem_frase_baixo_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_imagem_padrao = models.ForeignKey(
        'ImagemPadrao',
        related_name='active_imagem_padrao_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_contactos_site = models.ForeignKey(
        'ContactosSite',
        related_name='active_contactos_site_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_google_maps = models.ForeignKey(
        'GoogleMaps',
        related_name='active_google_maps_set',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    active_horario = models.ManyToManyField(
        'Horario',
        related_name='active_horario_set',
        blank=True,
    )

    def __str__(self):
        return 'Configurações ativas'


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
