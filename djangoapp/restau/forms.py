from django import forms
from . import models


class ProductForm(forms.ModelForm):
    picture = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        required=False,
    )

    class Meta:
        model = models.Products
        fields = (
            'image', 'nome', 'descricao_curta', 'descricao_longa',
            'preco', 'preco_promo', 'percentagem_desconto',
            'categoria', 'subcategoria', 'visibilidade',


        )
