# djangoapp/perfil/forms_auth.py
from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from djangoapp.fidelidade.models import RespostaFidelidade
from djangoapp.perfil.models import Perfil

User = get_user_model()


class RegisterForm(forms.Form):
    """Registration form with email + password only."""

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Palavra-passe",
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirmar palavra-passe",
    )

    def clean_email(self) -> str:
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este email já existe.")
        return email

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean() or {}
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "As palavras-passe não coincidem.")

        if p1:
            try:
                # Uses AUTH_PASSWORD_VALIDATORS from settings.py
                validate_password(p1)
            except DjangoValidationError as e:
                self.add_error("password1", e)

        return cleaned


class OnboardingPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ("telemovel", "data_nascimento", "estudante")
        widgets = {
            "telemovel": forms.TextInput(attrs={"class": "form-control"}),
            "data_nascimento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    estudante = forms.ModelChoiceField(
        queryset=RespostaFidelidade.objects.all().order_by("id"),
        required=False,
        label="Estudante",
        help_text="Opcional (se aplicável).",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean() or {}
        telemovel = cleaned.get("telemovel")
        data_nascimento = cleaned.get("data_nascimento")

        errors: dict[str, str] = {}

        if telemovel:
            if len(telemovel) != 9 or not telemovel.isdigit():
                errors["telemovel"] = "O telemóvel tem de ter 9 dígitos."
            else:
                qs = Perfil.objects.filter(telemovel=telemovel).exclude(pk=self.instance.pk)
                if qs.exists():
                    errors["telemovel"] = "Este número de telemóvel já existe."

        if data_nascimento and data_nascimento > timezone.now().date():
            errors["data_nascimento"] = "Data de nascimento inválida."

        if errors:
            raise forms.ValidationError(errors)
        return cleaned


class LoginForm(forms.Form):
    """
    Login form with email or username and password.
    """

    identifier = forms.CharField(
        required=True,
        label="Email ou utilizador",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        required=True,
        label="Palavra-passe",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )