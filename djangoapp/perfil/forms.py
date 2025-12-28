# djangoapp/perfil/forms.py
from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.utils.safestring import mark_safe

from djangoapp.fidelidade.models import RespostaFidelidade
from djangoapp.perfil.models import Perfil

User = get_user_model()

class RegisterForm(forms.Form):
    """Registration form with email + password only."""

    email = forms.EmailField(required=True, label="Email")
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label="Palavra-passe",
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label="Confirmar palavra-passe",
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já existe.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "As palavras-passe não coincidem.")

        # Only validate password strength if we have a password
        if p1:
            try:
                # Configuration in settings.py(AUTH_PASSWORD_VALIDATORS)
                validate_password(p1)
            except forms.ValidationError as e:
                self.add_error("password1", e)

        return cleaned

class OnboardingPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ("telemovel", "data_nascimento", "estudante")

        widgets = {
            "data_nascimento": forms.DateInput(attrs={"type": "date"}),
        }

    estudante = forms.ModelChoiceField(
        queryset=RespostaFidelidade.objects.all(),
        required=False,
        label="Estudante",
        help_text="Opcional (se aplicável).",
    )

    def clean(self):
        cleaned = super().clean()
        telemovel = cleaned.get("telemovel")
        data_nascimento = cleaned.get("data_nascimento")

        errors = {}

        if telemovel:
            if len(telemovel) != 9 or not telemovel.isdigit():
                errors["telemovel"] = "O telemóvel tem de ter 9 dígitos."

            # unique per profile (excluding current)
            qs = Perfil.objects.filter(telemovel=telemovel).exclude(pk=self.instance.pk)
            if qs.exists():
                errors["telemovel"] = "Este número de telemóvel já existe."

        if data_nascimento and data_nascimento > timezone.now().date():
            errors["data_nascimento"] = "Data de nascimento inválida."

        if errors:
            raise forms.ValidationError(errors)
        return cleaned

class PerfilForm(forms.ModelForm):
    '''
    Profile Form
    '''
    class Meta:
        '''
        Meta Class
        '''
        model = Perfil
        fields = '__all__'
        exclude = (
            'usuario', 'numero_cliente', 'created_at',
            'updated_at', 'nif', 'qr_code', 'tipo_fidelidade',
            'ultima_atualizacao_data_nascimento', 'ultima_actividade',
            'reset_password_code', 'reset_password_code_expires',
            'data_cancelamento','notificacoes_email',
            'notificacoes_telemovel', 'first_login'
        )



        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }

    data_nascimento = forms.DateField(
        required=True,
        label='Data de Nascimento',
        help_text='Importante! A data de nascimento é necessária para a \
            atribuição de pontos de fidelidade. Só é possível alterar \
                a data de nascimento uma vez por ano.',
        widget=forms.DateInput(
            attrs={'type': 'date'}
        ),
    )

    telemovel = forms.CharField(
        required=True,
        label='Telemóvel',
        help_text='Número de telemóvel para contacto.',
    )

    estudante = forms.ModelChoiceField(
        queryset=RespostaFidelidade.objects.all(),
        required=True,
        label='Estudante',
        help_text='Selecione uma resposta.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label_suffix = mark_safe(
                    '<span class="asteriskField">*</span>')
            else:
                field.label_suffix = ''

    def clean(self, *args, **kwargs):
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        data_nascimento_data = cleaned.get('data_nascimento')
        telemovel_data = cleaned.get('telemovel')

        error_msg_data_nascimento = 'Data de nascimento inválida.'
        error_msg_telemovel = 'Número de telemóvel tem de ter 9 digitos.'
        error_msg_telemovel_existe = 'Este número de telemóvel já existe.'

        if data_nascimento_data:
            if data_nascimento_data > timezone.now().date():
                validation_error_msgs['data_nascimento'] = error_msg_data_nascimento

        if telemovel_data:
            if len(telemovel_data) != 9:
                validation_error_msgs['telemovel'] = error_msg_telemovel

            # verificação se estamos a atualizar uma instância exixtente
            if self.instance.id is not None:
                telemovel_db = Perfil.objects.filter(
                    telemovel=telemovel_data).exclude(
                        id=self.instance.id).first()
            else:
                telemovel_db = Perfil.objects.filter(
                    telemovel=telemovel_data).first()
            if telemovel_db:
                validation_error_msgs['telemovel'] = error_msg_telemovel_existe
        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password', 'password2', 'email')

    username = forms.CharField(
        min_length=3,
        max_length=30,
        required=True,
        label='Utilizador',
        help_text='Importante! O utilizador não pode ser alterado.'
    )


    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nome',
        help_text='Seu nome.'
    )


    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apelido',
        help_text='Seu apelido.'
    )


    email = forms.EmailField(
        required=True,
        label='Endereço de email',
        help_text='Seu endereço de email.'
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Palavra-passe',
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Confirmação Palavra-passe',
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        updating = kwargs.pop('updating', False)
        super(UserForm, self).__init__(*args, **kwargs)

        self.usuario = usuario

        self.updating = updating

        if self.updating:

            # se estiver a atualizar remover os campos de password
            self.fields.pop('password')
            self.fields.pop('password2')

        if usuario:
            self.fields['username'].widget.attrs['readonly'] = True

        for field_name, field in self.fields.items():
            if field.required:
                field.label_suffix = mark_safe(
                    ' <span class="asteriskField">*</span>')
            else:
                field.label_suffix = ''

    def clean(self, *args, **kwargs):
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        usuario_data = cleaned.get('username')
        email_data = cleaned.get('email')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')

        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_user_exists = 'Este nome de usuário já existe.'
        error_msg_email_exists = 'Este email já existe.'
        error_msg_passwords_not_match = 'As palavras-passe não coincidem.'
        error_msg_password_short = (
            'A palavra-passe deve ter no mínimo 6 caracteres.'
        )
        error_msg_required = 'Este campo é obrigatório.'

        # Usúarios logados: Actualização
        if self.usuario:
            if usuario_db:
                if usuario_data != usuario_db.username:
                    validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msgs['email'] = error_msg_email_exists

            if password_data:
                if password_data != password2_data:
                    validation_error_msgs['password'] = error_msg_passwords_not_match
                    validation_error_msgs['password2'] = error_msg_passwords_not_match

                if password_data is not None and len(password_data) < 6:
                    validation_error_msgs['password'] = error_msg_password_short

        # Usúarios não logados: Criação
        else:
            if usuario_db:
                validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                validation_error_msgs['email'] = error_msg_email_exists

            if not password_data:
                validation_error_msgs['password'] = error_msg_required

            if not password2_data:
                validation_error_msgs['password2'] = error_msg_required

            if password_data != password2_data:
                validation_error_msgs['password'] = (
                    error_msg_passwords_not_match
                )
                validation_error_msgs['password2'] = (
                    error_msg_passwords_not_match
                )

            if password_data is not None and len(password_data) < 6:
                validation_error_msgs['password'] = error_msg_password_short

        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))

        if self.usuario and 'username' in self.changed_data:
            validation_error_msgs['username'] = 'O utilizador não pode \
            ser alterado.'


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Palavra-passe',
        help_text='Escolha Password.'
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Confirmação Palavra-passe',
        help_text='Confirme Password.'
    )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()
        validation_error_msgs = {}

        password_data = cleaned_data.get('password')
        password2_data = cleaned_data.get('password2')

        error_msg_passwords_not_match = 'As palavras-passe não coincidem.'
        error_msg_password_short = (
            'A palavra-passe deve ter no mínimo 6 caracteres.'
        )
        if password_data:
            if len(password_data) < 6:
                validation_error_msgs['password'] = error_msg_password_short

            if password_data != password2_data:
                validation_error_msgs['password'] = error_msg_passwords_not_match
                validation_error_msgs['password2'] = error_msg_passwords_not_match

        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))


class RequestResetPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label='Endereço de email',
        help_text='Seu endereço de email.'
    )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()
        validation_error_msgs = {}

        email_data = cleaned_data.get('email')

        error_msg_email_not_exists = 'Este email não existe.'

        email_db = User.objects.filter(email=email_data).first()

        if not email_db:
            validation_error_msgs['email'] = error_msg_email_not_exists

        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))
        return cleaned_data


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Palavra-passe',
        help_text='Escolha Password.'
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Confirmação Palavra-passe',
        help_text='Confirme Password.'
    )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()
        validation_error_msgs = {}

        password_data = cleaned_data.get('password')
        password2_data = cleaned_data.get('password2')

        error_msg_passwords_not_match = 'As palavras-passe não coincidem.'
        error_msg_password_short = (
            'A palavra-passe deve ter no mínimo 6 caracteres.'
        )
        if password_data:
            if len(password_data) < 6:
                validation_error_msgs['password'] = error_msg_password_short

            if password_data != password2_data:
                validation_error_msgs['password'] = error_msg_passwords_not_match
                validation_error_msgs['password2'] = error_msg_passwords_not_match

        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))
