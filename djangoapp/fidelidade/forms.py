from __future__ import annotations

from typing import cast

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from djangoapp.fidelidade.models import (
    ComprasFidelidade,
    Fidelidade,
    OfertasFidelidade,
    Products,
    ProdutoFidelidadeIndividual,
)


class FidelidadeForm(forms.ModelForm):
    nome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "digite aqui",
            }
        ),
        label="Nome",
        help_text="Nome da fidelidade.",
    )

    desconto = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "digite aqui",
            }
        ),
        label="Desconto",
        help_text="Desconto a aplicar.",
    )

    class Meta:
        model = Fidelidade
        fields = (
            "nome",
            "desconto",
            "ementa",
        )

    def clean(self):
        cleaned_data = super().clean()

        nome = cleaned_data.get("nome")
        desconto_raw = cleaned_data.get("desconto")
        instance = self.instance

        # Nome duplicado (ignora o próprio registo em edição)
        if nome and (not instance or instance.nome != nome):
            if Fidelidade.objects.filter(nome=nome).exists():
                self.add_error(
                    "nome",
                    ValidationError("A fidelidade já existe.", code="invalid"),
                )

        # Desconto é obrigatório (o mypy quer isto explícito)
        if desconto_raw is None:
            self.add_error(
                "desconto",
                ValidationError("Tem de ter um desconto.", code="invalid"),
            )
            return cleaned_data

        desconto = int(desconto_raw)

        # Se queres impedir descontos repetidos, usa exists()
        # (ignora o próprio registo em edição)
        qs = Fidelidade.objects.filter(desconto=desconto)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            self.add_error(
                "desconto",
                ValidationError("Já existe uma fidelidade com esse desconto.", code="invalid"),
            )

        return cleaned_data


class ProdutoFidelidadeIndividualForm(forms.ModelForm):
    class Meta:
        model = ProdutoFidelidadeIndividual
        fields = [
            "fidelidade",
            "produto",
            "pontos_recompensa",
            "pontos_para_oferta",
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
                "readonly": "readonly",
            }
        ),
        label="Pontos Recompensa",
        help_text="Pontos Recompensa.",
        required=False,
    )

    pontos_para_oferta = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "readonly": "readonly",
            }
        ),
        label="Pontos para Oferta",
        help_text="Pontos para Oferta.",
        required=False,
    )

    visibilidade = forms.BooleanField(
        widget=forms.CheckboxInput(),
        label="Visibilidade",
        help_text="Visibilidade.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        fidelidade_id = kwargs.pop("fidelidade_id", None)
        super().__init__(*args, **kwargs)

        if fidelidade_id:
            fidelidade_instance = Fidelidade.objects.get(pk=fidelidade_id)

            fidelidade_field = cast(forms.ModelChoiceField, self.fields["fidelidade"])
            fidelidade_field.queryset = Fidelidade.objects.filter(
                ementa__fidelidade__pk=fidelidade_id
            )
            fidelidade_field.initial = fidelidade_instance

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.pk:
            original_instance = ProdutoFidelidadeIndividual.objects.get(pk=instance.pk)
            instance.pontos_recompensa = original_instance.pontos_recompensa
            instance.pontos_para_oferta = original_instance.pontos_para_oferta

        if commit:
            instance.save()
        return instance


class ComprasFidelidadeForm(forms.ModelForm):
    class Meta:
        model = ComprasFidelidade
        fields = [
            "fidelidade",
            "utilizador",
            "compra",
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
                "placeholder": "digite aqui",
            }
        ),
        label="Compra",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        fidelidade_id = kwargs.pop("fidelidade_id", None)
        utilizador_pk = kwargs.pop("utilizador_pk", None)
        super().__init__(*args, **kwargs)

        if fidelidade_id:
            fidelidade_instance = Fidelidade.objects.get(pk=fidelidade_id)

            fidelidade_field = cast(forms.ModelChoiceField, self.fields["fidelidade"])
            fidelidade_field.queryset = Fidelidade.objects.filter(
                ementa__fidelidade__pk=fidelidade_id
            )
            fidelidade_field.initial = fidelidade_instance

        if utilizador_pk:
            utilizador_instance = User.objects.get(pk=utilizador_pk)

            utilizador_field = cast(forms.ModelChoiceField, self.fields["utilizador"])
            utilizador_field.queryset = User.objects.filter(perfil__pk=utilizador_pk)
            utilizador_field.initial = utilizador_instance


class OfertasFidelidadeForm(forms.ModelForm):
    class Meta:
        model = OfertasFidelidade
        fields = [
            "fidelidade",
            "utilizador",
            "pontos_gastos",
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
                "placeholder": "digite aqui",
            }
        ),
        label="Pontos Gastos",
        help_text="Pontos Gastos.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        fidelidade_id = kwargs.pop("fidelidade_id", None)
        super().__init__(*args, **kwargs)

        if fidelidade_id:
            fidelidade_instance = Fidelidade.objects.get(pk=fidelidade_id)

            fidelidade_field = cast(forms.ModelChoiceField, self.fields["fidelidade"])
            fidelidade_field.queryset = Fidelidade.objects.filter(
                ementa__fidelidade__pk=fidelidade_id
            )
            fidelidade_field.initial = fidelidade_instance