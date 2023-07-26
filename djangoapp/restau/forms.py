from typing import Any, Dict
from django.core.exceptions import ValidationError
from django import forms
from restau.models import Products


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
        help_text='Nome do artigo.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Products
        fields = (
            'imagem', 'nome', 'descricao_curta', 'descricao_longa',
            'preco', 'preco_promo', 'percentagem_desconto',
            'categoria', 'subcategoria', 'visibilidade',


        )

    def clean(self):
        cleaned_data = self.cleaned_data
        nome = cleaned_data.get('nome')
        if Products.objects.filter(nome=nome).exists():

            self.add_error(
                'nome',
                ValidationError(
                    'O produto já existe.',
                    code='invalid'
                )
            )
        return super().clean()
