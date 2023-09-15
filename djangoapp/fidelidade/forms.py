from django import forms
from fidelidade.models import Fidelidade, ProdutoFidelidadeIndividual
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
