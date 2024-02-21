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

    desconto = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Desconto',
        help_text='Desconto a aplicar.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Fidelidade
        fields = (
            'nome', 'desconto', 'ementa',
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        nome = cleaned_data.get('nome')
        desconto = cleaned_data.get('desconto')
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

        if Fidelidade.objects.filter(desconto=desconto) is not None:
            return cleaned_data

        else:
            self.add_error(
                'desconto',
                ValidationError(
                    'Tem de ter um desconto.',
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

    pontos_recompensa = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                # 'placeholder': 'digite aqui',
                'readonly': 'readonly',
            }
        ),
        label='Pontos Recompensa',
        help_text='Pontos Recompensa.',
        required=False,
    )

    pontos_para_oferta = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                # 'placeholder': 'digite aqui',
                'readonly': 'readonly',
            }
        ),
        label='Pontos para Oferta',
        help_text='Pontos para Oferta.',
        required=False,
    )
    visibilidade = forms.BooleanField(
        widget=forms.CheckboxInput(),
        label='Visibilidade',
        help_text='Visibilidade.',
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.pk:
            original_instance = ProdutoFidelidadeIndividual.objects.get(
                pk=instance.pk)
            instance.pontos_recompensa = original_instance.pontos_recompensa
            instance.pontos_para_oferta = original_instance.pontos_para_oferta

        if commit:
            instance.save()
        return instance


class ComprasFidelidadeForm(forms.ModelForm):
    class Meta:
        model = ComprasFidelidade
        fields = [
            'fidelidade', 'utilizador',
            'compra', 'pontos_adicionados',
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

    compra = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'digite aqui',
            }
        ),
        label='Compra',
        help_text='Compra.',
        required=False,
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        compra = cleaned_data.get('compra')
        desconto = cleaned_data.get('fidelidade').desconto
        pontos_adicionados = round(compra * desconto / 100, 2)
        print('compra: ', compra)
        print('pontos_adicionados: ', pontos_adicionados)
        cleaned_data['pontos_adicionados'] = pontos_adicionados

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
        queryset=User.objects.all(),
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
