''' Modulo de formulários para o app restau. '''

from django.core.exceptions import ValidationError
from django import forms
from django.forms import modelformset_factory
from restau.models import (
    Category, SubCategory, Products, Ementa, ProdutosEmenta,
    Fotos, ImagemLogo, ImagemTopo, Intro, IntroImagem, FraseInspiradora,
    FraseCima, ImagemFraseCima, FraseBaixo, ImagemFraseBaixo, ImagemPadrao,
    ContactosSite, GoogleMaps, Horario
)


class SubCategoryForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Nome',
        help_text='Nome do artigo.'
    )

    ordem = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Ordem',
        help_text='Ordem do artigo.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = SubCategory
        fields = (
            'nome', 'categoria', 'ordem',
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        nome = cleaned_data.get('nome')
        instance = self.instance

        if instance and instance.nome == nome:
            return cleaned_data
        if SubCategory.objects.filter(nome=nome).exists():

            self.add_error(
                'nome',
                ValidationError(
                    'A subcategoria já existe.',
                    code='invalid'
                )
            )

        return super().clean()


class CategoryForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Nome',
        help_text='Nome do artigo.'
    )

    ordem = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Ordem',
        help_text='Ordem do artigo.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Category
        fields = (
            'nome', 'ordem',
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        nome = cleaned_data.get('nome')
        instance = self.instance

        if instance and instance.nome == nome:
            return cleaned_data
        if Category.objects.filter(nome=nome).exists():

            self.add_error(
                'nome',
                ValidationError(
                    'A categoria já existe.',
                    code='invalid'
                )
            )

        return super().clean()


class ProductForm(forms.ModelForm):
    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Fotografia',
        required=False,
    )

    nome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Produto',
        help_text='Nome do artigo.',
    )

    ordem = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Ordem',
        help_text='Ordem do artigo.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Products
        fields = (
            'imagem', 'nome', 'descricao_curta', 'descricao_longa',
            'preco_1', 'preco_2', 'preco_3', 'preco_4', 'preco_5', 'preco_6',
            'preco_promo', 'percentagem_desconto', 'categoria', 'subcategoria',
            'visibilidade', 'ordem',
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        nome = cleaned_data.get('nome')
        instance = self.instance

        if instance and instance.nome == nome:
            return cleaned_data
        if Products.objects.filter(nome=nome).exists():

            self.add_error(
                'nome',
                ValidationError(
                    'O produto já existe.',
                    code='invalid'
                )
            )

        return super().clean()


class EmentaForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nome da ementa',
            }
        ),
        label='Nome',
        help_text='Nome da ementa.'
    )
    descricao = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Descrição da ementa',
            }
        ),
        label='Descrição',
        help_text='Descrição da ementa.'
    )
    nome_campo_preco_selecionado = forms.ChoiceField(
        choices=[
            ('preco_1', 'Preço 1'),
            ('preco_2', 'Preço 2'),
            ('preco_3', 'Preço 3'),
            ('preco_4', 'Preço 4'),
            ('preco_5', 'Preço 5'),
            ('preco_6', 'Preço 6'),
        ],
        label='Preço',
        help_text='Preço na ementa.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Ementa
        fields = (
            'nome', 'descricao', 'nome_campo_preco_selecionado',
        )


class ProdutosEmentaForm(forms.Form): 
    produto = forms.ModelMultipleChoiceField(
        queryset=Products.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Produto',
        help_text='Produto.'
    )

    descricao = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Descrição do produto na ementa'}
        ),
        label='Descrição',
        help_text='Descrição do produto na ementa.',
        required=False
    )

    def __init__(self, *args, **kwargs):
        ementa_id = kwargs.pop('ementa_id', None)
        super().__init__(*args, **kwargs)

        if ementa_id:
            self.ementa_instance = Ementa.objects.get(pk=ementa_id)
        else:
            self.ementa_instance = None

    class Meta:
        model = ProdutosEmenta
        fields = (
            'ementa', 'produto', 'descricao',
        )


class FotosForm(forms.ModelForm):
    class Meta:
        model = Fotos
        fields = (
            'imagem', 'is_visible', 'ordem',
        )

    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Fotografia',
        required=False,
    )

    is_visible = forms.BooleanField(
        widget=forms.CheckboxInput(),
        label='Visíbilidade',
        help_text='Seleccionar se visível.',
        required=False,
    )

    ordem = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Ordem',
        help_text='Ordem da galeria.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


FotosFormSet = modelformset_factory(
    Fotos,
    form=FotosForm,
    extra=0,
    can_delete=True
)


class ImagemLogoForm(forms.ModelForm):
    class Meta:
        model = ImagemLogo
        fields = (
            'imagem',
        )

    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Logotipo',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


LogosFormSet = modelformset_factory(
    ImagemLogo,
    form=ImagemLogoForm,
    extra=0,
    can_delete=True,
    fields=(
        'imagem',
    )
)


class ImagemTopoForm(forms.ModelForm):
    class Meta:
        model = ImagemTopo
        fields = (
            'imagem',
        )

    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Fotografia',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


TopoFormSet = modelformset_factory(
    ImagemTopo,
    form=ImagemTopoForm,
    extra=0,
    can_delete=True,
    fields=(
        'imagem',
    )
)


class IntroForm(forms.ModelForm):
    class Meta:
        model = Intro
        fields = (
            'texto',
        )

    texto = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Texto',
        help_text='Introduçao.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


IntroFormSet = modelformset_factory(
    Intro,
    form=IntroForm,
    extra=0,
    can_delete=True,
    fields=(
        'texto',
    )
)


class IntroImagemForm(forms.ModelForm):
    class Meta:
        model = IntroImagem
        fields = (
            'imagem',
        )

    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Imagem para introdução',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


IntroImagemFormSet = modelformset_factory(
    IntroImagem,
    form=IntroImagemForm,
    extra=0,
    can_delete=True,
    fields=(
        'imagem',
    )
)


class FraseInspiradoraForm(forms.ModelForm):
    class Meta:
        model = FraseInspiradora
        fields = (
            'texto',
        )

    texto = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Texto',
        help_text='Frase central.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


FraseInspiradoraFormSet = modelformset_factory(
    FraseInspiradora,
    form=FraseInspiradoraForm,
    extra=0,
    can_delete=True,
    fields=(
        'texto',
    )
)


class FraseCimaForm(forms.ModelForm):
    class Meta:
        model = FraseCima
        fields = (
            'texto',
        )

    texto = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Frase',
        help_text='Frase Cima.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


FraseCimaFormSet = modelformset_factory(
    FraseCima,
    form=FraseCimaForm,
    extra=0,
    can_delete=True,
    fields=(
        'texto',
    )
)


class ImagemFraseCimaForm(forms.ModelForm):
    class Meta:
        model = ImagemFraseCima
        fields = (
            'imagem',
        )

    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Imagem para frase cima',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ImagemFraseCimaFormSet = modelformset_factory(
    ImagemFraseCima,
    form=ImagemFraseCimaForm,
    extra=0,
    can_delete=True,
    fields=(
        'imagem',
    )
)


class FraseBaixoForm(forms.ModelForm):
    class Meta:
        model = FraseBaixo
        fields = (
            'texto',
        )

    texto = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Frase',
        help_text='Frase Baixo.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


FraseBaixoFormSet = modelformset_factory(
    FraseBaixo,
    form=FraseBaixoForm,
    extra=0,
    can_delete=True,
    fields=(
        'texto',
    )
)


class ImagemFraseBaixoForm(forms.ModelForm):
    class Meta:
        model = ImagemFraseBaixo
        fields = (
            'imagem',
        )

    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Imagem para frase baixo',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ImagemFraseBaixoFormSet = modelformset_factory(
    ImagemFraseBaixo,
    form=ImagemFraseBaixoForm,
    extra=0,
    can_delete=True,
    fields=(
        'imagem',
    )
)


class ImagemPadraoForm(forms.ModelForm):
    class Meta:
        model = ImagemPadrao
        fields = (
            'imagem',
        )

    imagem = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        label='Imagem padrão',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ImagemPadraoFormSet = modelformset_factory(
    ImagemPadrao,
    form=ImagemPadraoForm,
    extra=0,
    can_delete=True,
    fields=(
        'imagem',
    )
)


class ContactosSiteForm(forms.ModelForm):
    class Meta:
        model = ContactosSite
        fields = (
            'morada', 'telefone', 'email', 'facebook', 'facebook_icon',
            'instagram', 'instagram_icon',
        )

    telefone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Telefone',
        help_text='Telefone.',
    )

    morada = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Morada',
        help_text='Morada.',
    )

    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Email',
        help_text='Email.',
    )

    facebook = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Facebook',
        help_text='Facebook.',
    )

    facebook_icon = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Facebook Icon',
        help_text='Facebook Icon.',
    )

    instagram = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Instagram',
        help_text='Instagram.',
    )

    instagram_icon = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Instagram Icon',
        help_text='Instagram Icon.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GoogleMapsForm(forms.ModelForm):
    class Meta:
        model = GoogleMaps
        fields = (
            'iframe',
        )

    iframe = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Google Maps',
        help_text='Google Maps.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = (
            'dia_semana', 'hora_abertura_almoco', 'hora_fecho_almoco',
            'hora_abertura_jantar', 'hora_fecho_jantar', 'status',
        )

    dia_semana = forms.ChoiceField(
        choices=[
            ('Segunda', 'Segunda-feira'),
            ('Terça', 'Terça-feira'),
            ('Quarta', 'Quarta-feira'),
            ('Quinta', 'Quinta-feira'),
            ('Sexta', 'Sexta-feira'),
            ('Sábado', 'Sábado'),
            ('Domingo', 'Domingo'),
            ('Feriados', 'Feriados')
        ],
        label='Dia da semana',
        help_text='Dia da semana.',
    )

    hora_abertura_almoco = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Hora de abertura para almoço',
        help_text='Formato: 00:00',
        required=False,
    )

    hora_fecho_almoco = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Hora de fecho para almoço',
        help_text='Formato: 00:00',
        required=False,
    )

    hora_abertura_jantar = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Hora de abertura para jantar',
        help_text='Formato: 00:00',
        required=False,
    )

    hora_fecho_jantar = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Hora de fecho para jantar',
        help_text='Formato: 00:00',
        required=False,
    )

    status = forms.ChoiceField(
        choices=[
            ('Aberto', 'Aberto'),
            ('Encerrado', 'Encerrado'),
        ],
        label='Estado',
        help_text='Estado.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
