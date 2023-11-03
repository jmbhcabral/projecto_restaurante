from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from perfil.models import Perfil
# from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class PerfilSerializer(ModelSerializer):
    usuario = UserSerializer()
    qrcode_url = SerializerMethodField()

    class Meta:
        model = Perfil
        fields = ('usuario', 'data_nascimento',
                  'telemovel', 'estudante', 'qrcode_url')

    def get_qrcode_url(self, obj):
        request = self.context.get('request')
        if request:
            qrcode_url = obj.qr_code.url if obj.qr_code else None
            return request.build_absolute_uri(
                qrcode_url) if qrcode_url else None

    def update(self, instance, validated_data):
        user_data = validated_data.pop('usuario', None)
        user_serializer = UserSerializer(
            instance.usuario, data=user_data, partial=True)
        if user_serializer.is_valid(raise_exception=True):
            user_serializer.save()
        return super().update(instance, validated_data)


class UserRegistrationSerializer(ModelSerializer):
    perfil = PerfilSerializer()

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password',
            'perfil', 'id'
        )

    def validate_email(self, value):
        # Se estamos criando um novo usuário ou atualizando o e-mail de um
        # existente, verificar unicidade.
        if not self.instance or (self.instance.email != value):
            if get_user_model().objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    'Já existe um usuário com este e-mail.')
        return value

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

        # Validação do Nome
        if not data.get('first_name'):
            errors['first_name'] = 'O campo Nome é obrigatório.'

        # Validação do Sobrenome
        if not data.get('last_name'):
            errors['last_name'] = 'O campo Sobrenome é obrigatório.'

        perfil_data = data.get('perfil')
        if perfil_data:
            if 'telemovel' not in perfil_data:
                errors['perfil.telemovel'] = 'O campo telemovel é obrigatório.'
            if 'telemovel' in perfil_data and \
                    len(perfil_data['telemovel']) < 9:
                errors['perfil.telemovel'] = 'O campo telemovel é inválido.'

            if 'data_nascimento' not in perfil_data:
                errors['perfil.data_nascimento'] = (
                    'O campo data de nascimento é obrigatório.'
                )

            if 'estudante' not in perfil_data:
                errors['perfil.estudante'] = 'O campo estudante é obrigatório.'

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
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()

        perfil_data = validated_data.get('perfil')
        if perfil_data:
            perfil, _ = Perfil.objects.get_or_create(usuario=instance)
            perfil.data_nascimento = perfil_data.get(
                'data_nascimento', perfil.data_nascimento)
            perfil.telemovel = perfil_data.get(
                'telemovel', perfil.telemovel)
            perfil.estudante = perfil_data.get(
                'estudante', perfil.estudante)
            perfil.save()

            return instance


class UserPerfilSerializer(serializers.ModelSerializer):
    perfil_data = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name',
                  'last_name', 'perfil_data')

    def get_perfil_data(self, obj):
        perfil = Perfil.objects.get(usuario=obj)
        return {
            'data_nascimento': perfil.data_nascimento,
            'telemovel': perfil.telemovel,
            'estudante': perfil.estudante,
            'qrcode_url': perfil.qr_code.url if perfil.qr_code else None,

        }
