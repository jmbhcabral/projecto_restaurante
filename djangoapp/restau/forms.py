from django.core.exceptions import ValidationError
from django import forms
from restau.models import (Products, Category, SubCategory, Ementa,
                           ProdutosEmenta, Fotos,
                           )
from django.forms import modelformset_factory


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
        if Products.objects.filter(nome=nome).exists():

            self.add_error(
                'nome',
                ValidationError(
                    'O produto já existe.',
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
        if Products.objects.filter(nome=nome).exists():

            self.add_error(
                'nome',
                ValidationError(
                    'O produto já existe.',
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


class ProdutosEmentaForm(forms.ModelForm):
    ementa = forms.ModelChoiceField(
        queryset=Ementa.objects.none(),  # Empty by default
        widget=forms.HiddenInput(),
        # label='Ementa',
        # help_text='Ementa.'
    )
    produto = forms.ModelMultipleChoiceField(
        queryset=Products.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Produto',
        help_text='Produto.'
    )

    def __init__(self, *args, **kwargs):
        ementa_id = kwargs.pop('ementa_id', None)
        super(ProdutosEmentaForm, self).__init__(*args, **kwargs)
        if ementa_id:
            ementa_instance = Ementa.objects.get(pk=ementa_id)
            self.fields['ementa'].queryset = Ementa \
                .objects \
                .filter(
                pk=ementa_id
            )
            # Setting the initial value
            self.fields['ementa'].initial = ementa_instance

    class Meta:
        model = ProdutosEmenta
        fields = (
            'ementa', 'produto',
        )


class FotosForm(forms.ModelForm):
    class Meta:
        model = Fotos
        fields = (
            'imagem', 'is_visible',
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

    # nome = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             'readonly': True,
    #         }
    #     ),
    #     label='Nome',
    #     help_text='Nome da fotografia.',
    # )

    is_visible = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Visíbilidade',
        help_text='Seleccionar se visível.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


FotosFormSet = modelformset_factory(
    Fotos,
    form=FotosForm,
    extra=0,
    can_delete=True
)
