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
        required=False,
    )

    class Meta:
        model = Products
        fields = (
            'imagem', 'nome', 'descricao_curta', 'descricao_longa',
            'preco', 'preco_promo', 'percentagem_desconto',
            'categoria', 'subcategoria', 'visibilidade',


        )

    def clean(self):
        cleaned_data = self.cleaned_data

        self.add_error(
            'nome',
            ValidationError(
                'Mensagem de erro',
                code='invalid'
            )
        )
        return super().clean()
