from django import forms
from fidelidade.models import (Fidelidade, Ementa,
                               ProdutoFidelidadeIndividual, Products)
from django.core.exceptions import ValidationError


class FidelidadeForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Nome',
        help_text='Nome da fidelidade.'
    )

    unidade = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Unidade',
        help_text='Unidade por Euro.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Fidelidade
        fields = (
            'nome', 'unidade', 'ementa',
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        nome = cleaned_data.get('nome')
        instance = self.instance

        if instance and instance.nome == nome:
            return cleaned_data
        if Fidelidade.objects.filter(nome=nome).exists():

            self.add_error(
                'nome',
                ValidationError(
                    'A fidelidade já existe.',
                    code='invalid'
                )
            )

        return super().clean()


class ProdutoFidelidadeIndividualForm(forms.ModelForm):
    class Meta:
        model = ProdutoFidelidadeIndividual
        fields = [
            'fidelidade', 'ementa', 'produto',
            'pontos_recompensa', 'pontos_para_oferta',
        ]

    fidelidade = forms.ModelChoiceField(
        queryset=Fidelidade.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    ementa = forms.ModelChoiceField(
        queryset=Ementa.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    produto = forms.ModelChoiceField(
        queryset=Products.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    pontos_recompensa = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Pontos Recompensa',
        help_text='Pontos Recompensa.',
        required=False,
    )

    pontos_para_oferta = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Pontos para Oferta',
        help_text='Pontos para Oferta.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.fidelidade_id = kwargs.pop('fidelidade_id', None)
        super().__init__(*args, **kwargs)

        if hasattr(self.instance, 'fidelidade'):
            self.fields['fidelidade'].initial = self.instance.fidelidade
            self.fields['fidelidade'].disabled = True  # Campo não editável

        if hasattr(self.instance, 'ementa'):
            self.fields['ementa'].initial = self.instance.ementa
            self.fields['ementa'].disabled = True  # Campo não editável

        if hasattr(self.instance, 'produto'):
            self.fields['produto'].initial = self.instance.produto
            self.fields['produto'].disabled = True  # Campo não editável
