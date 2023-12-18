from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from perfil.models import Perfil
# from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
import logging
from django.contrib.auth.hashers import check_password

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class PerfilSerializer(ModelSerializer):
    qrcode_url = SerializerMethodField()

    class Meta:
        model = Perfil
        fields = ('data_nascimento',
                  'telemovel', 'estudante', 'qrcode_url')

    def validate_telemovel(self, value):
        perfil_instance = self.context.get('perfil_instance')
        # Ignora a validação se estiver atualizando o perfil atual
        print('perfil_instance validate_telemovel: ', perfil_instance)
        if perfil_instance and perfil_instance.telemovel == value:
            return value

        print('existe telemovel: ', Perfil.objects.filter(telemovel=value).exclude(
            pk=perfil_instance.pk if perfil_instance else None).exists())
        print('telemovel: ', value)

        if perfil_instance:
            print('Self.instance.pk: ', perfil_instance.pk)
        else:
            print('Não existe self.instance.pk')
        # Verifica se o número de telemóvel já está em uso
        if Perfil.objects.filter(telemovel=value).exclude(
                pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError(
                'Este número de telemóvel já está em uso.', value)

        return value

    def validate(self, data):
        errors = {}

        # Validação do telemovel
        if 'telemovel' not in data:
            errors['telemovel'] = 'O campo telemovel é obrigatório.'
        elif len(data['telemovel']) != 9:
            errors['telemovel'] = 'O campo telemovel é inválido.'

        # Validação da data de nascimento
        if 'data_nascimento' not in data:
            errors['data_nascimento'] = (
                'O campo data de nascimento é obrigatório.')

        # Validação do campo estudante
        if 'estudante' not in data:
            errors['estudante'] = 'O campo estudante é obrigatório.'

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def get_qrcode_url(self, obj):
        request = self.context.get('request')
        if request:
            qrcode_url = obj.qr_code.url if obj.qr_code else None
            return request.build_absolute_uri(
                qrcode_url) if qrcode_url else None

    def update(self, instance, validated_data):
        pass


class UserRegistrationSerializer(ModelSerializer):
    perfil = PerfilSerializer()
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password',
            'perfil', 'id'
        )

    def validate_username(self, value):
        # Verifica se estamos criando um novo usuário ou atualizando um
        # existente
        if not self.instance or (
                self.instance and self.instance.username != value):
            if get_user_model().objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    'Este nome de utilizador já está em uso.')
        return value

    def validate_email(self, value):
        # Se estamos criando um novo usuário ou atualizando o e-mail de um
        # existente, verificar unicidade.
        if not self.instance or (self.instance.email != value):
            if get_user_model().objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    'Já existe um utilizador com este e-mail.')
        return value

    def validate_password(self, value):
        # Se não estiver atualizando um usuário, simplesmente retorne o valor
        if not self.instance:
            return value

        # Se estiver atualizando e a senha for diferente da armazenada
        if self.instance and not check_password(value, self.instance.password):
            # Aqui você pode adicionar validação adicional, como comprimento da senha
            if len(value) < 8:
                raise serializers.ValidationError(
                    'A senha deve conter pelo menos 8 caracteres.')
            return value

        # Se a senha fornecida for a mesma que a armazenada, ignore a atualização
        raise serializers.SkipField()

    def validate(self, data):
        errors = {}

        # Validação do email
        email = data.get('email')
        if email is None or email == '':
            errors['email'] = 'O campo email é obrigatório.'

        else:
            try:
                django_validate_email(email)
            except DjangoValidationError:
                errors['email'] = 'O email informado é inválido.'

        if self.instance and self.instance.email != email:
            if get_user_model().objects.exclude(
                    pk=self.instance.pk).filter(email=email).exists():
                errors['email'] = 'Este email já está em uso.'
        print('Data def validate: ', data)
        # Validação do Nome
        if not data.get('first_name'):
            errors['first_name'] = 'O campo Nome é obrigatório.'

        # Validação do Sobrenome
        if not data.get('last_name'):
            errors['last_name'] = 'O campo Sobrenome é obrigatório.'

        # Validação do username
        if not data.get('username'):
            errors['username'] = 'O campo username é obrigatório.'
        # Validação do password
        if not self.instance and 'password' not in data:
            errors['password'] = 'O campo password é obrigatório.'

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil', None)

        user = get_user_model().objects.create_user(    # type: ignore
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()
        if perfil_data:
            Perfil.objects.create(usuario=user, **perfil_data)

        return user

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})

        # Atualizar os dados do utilizador
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Atualizar o perfil do utilizador
        perfil_instance = getattr(instance, 'perfil', None)
        if perfil_instance:
            for attr, value in perfil_data.items():
                setattr(perfil_instance, attr, value)
            perfil_instance.save()

        return instance
