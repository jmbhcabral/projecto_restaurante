from django import forms
from django.contrib.auth.models import User
from perfil.models import Perfil
from . import models
from django.utils import timezone


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario', 'numero_cliente', 'created_at',
                   'updated_at', 'nif', 'qr_code', 'tipo_fidelidade',
                   'ultima_atualizacao_data_nascimento')

        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        data_nascimento_data = cleaned.get('data_nascimento')
        telemovel_data = cleaned.get('telemovel')

        error_msg_data_nascimento = 'Data de nascimento inválida.'
        error_msg_telemovel = 'Número de telemóvel tem de ter 9 digitos.'
        error_msg_telemovel_existe = 'Este número de telemóvel já existe.'

        if data_nascimento_data:
            if data_nascimento_data > timezone.now().date():
                validation_error_msgs['data_nascimento'] = \
                    error_msg_data_nascimento

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
                validation_error_msgs['telemovel'] = \
                    error_msg_telemovel_existe
        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Palavra-passe',
        # help_text='Deixe em branco para não alterar.'
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmação Palavra-passe',
        # help_text='Deixe em branco para não alterar.'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

        if usuario:
            self.fields['username'].widget.attrs['readonly'] = True

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password', 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
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
                    validation_error_msgs['password'] = \
                        error_msg_passwords_not_match
                    validation_error_msgs['password2'] = \
                        error_msg_passwords_not_match

                if len(password_data) < 6:
                    validation_error_msgs['password'] = \
                        error_msg_password_short

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
                validation_error_msgs['password'] = \
                    error_msg_passwords_not_match
                validation_error_msgs['password2'] = \
                    error_msg_passwords_not_match

            if len(password_data) < 6:
                validation_error_msgs['password'] = \
                    error_msg_password_short

        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))

        if self.usuario and 'username' in self.changed_data:
            validation_error_msgs['username'] = 'O utilizador não pode \
            ser alterado.'
