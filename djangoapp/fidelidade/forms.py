from django import forms
from django.contrib.auth.models import User
from fidelidade.models import (
    Fidelidade, ProdutoFidelidadeIndividual, Products,
    ComprasFidelidade, OfertasFidelidade)
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
            'fidelidade', 'produto',
            'pontos_recompensa', 'pontos_para_oferta',
        ]

    fidelidade = forms.ModelChoiceField(
        queryset=Fidelidade.objects.all(),
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
        fidelidade_id = kwargs.pop('fidelidade_id', None)
        super(ProdutoFidelidadeIndividualForm, self).__init__(*args, **kwargs)
        if fidelidade_id:
            fidelidade_instance = Fidelidade.objects.get(pk=fidelidade_id)
            print('Fidelidade_capturada_form: ', fidelidade_instance)
            self.fields['fidelidade'].queryset = Fidelidade.objects.filter(
                ementa__fidelidade__pk=fidelidade_id)

            self.fields['fidelidade'].initial = fidelidade_instance


class ComprasFidelidadeForm(forms.ModelForm):
    class Meta:
        model = ComprasFidelidade
        fields = [
            'fidelidade', 'utilizador',
            'pontos_adicionados',
        ]

    fidelidade = forms.ModelChoiceField(
        queryset=Fidelidade.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    utilizador = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    pontos_adicionados = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Pontos Adicionados',
        help_text='Pontos Adicionados.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        fidelidade_id = kwargs.pop('fidelidade_id', None)
        utilizador_pk = kwargs.pop('utilizador_pk', None)
        super(ComprasFidelidadeForm, self).__init__(*args, **kwargs)
        if fidelidade_id:
            fidelidade_instance = Fidelidade.objects.get(pk=fidelidade_id)
            print('Fidelidade_capturada_form: ', fidelidade_instance)
            self.fields['fidelidade'].queryset = Fidelidade.objects.filter(
                ementa__fidelidade__pk=fidelidade_id)

            self.fields['fidelidade'].initial = fidelidade_instance
        if utilizador_pk:
            utilizador_instance = User.objects.get(pk=utilizador_pk)
            print('Utilizador_capturado_form: ', utilizador_instance)
            self.fields['utilizador'].queryset = User.objects.filter(
                perfil__pk=utilizador_pk)

            self.fields['utilizador'].initial = utilizador_instance


class OfertasFidelidadeForm(forms.ModelForm):
    class Meta:
        model = OfertasFidelidade
        fields = [
            'fidelidade', 'utilizador',
            'pontos_gastos',
        ]

    fidelidade = forms.ModelChoiceField(
        queryset=Fidelidade.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    utilizador = forms.ModelChoiceField(
        queryset=Products.objects.all(),
        widget=forms.HiddenInput(),
        required=False,
    )

    pontos_gastos = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Pontos Gastos',
        help_text='Pontos Gastos.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        fidelidade_id = kwargs.pop('fidelidade_id', None)
        super(OfertasFidelidadeForm, self).__init__(*args, **kwargs)
        if fidelidade_id:
            fidelidade_instance = Fidelidade.objects.get(pk=fidelidade_id)
            print('Fidelidade_capturada_form: ', fidelidade_instance)
            self.fields['fidelidade'].queryset = Fidelidade.objects.filter(
                ementa__fidelidade__pk=fidelidade_id)

            self.fields['fidelidade'].initial = fidelidade_instance
