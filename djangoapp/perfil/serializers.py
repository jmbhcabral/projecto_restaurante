from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from perfil.models import Perfil
# from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
from django.utils import timezone
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
    ultima_atualizacao_data_nascimento = serializers.DateTimeField(
        read_only=True)
    tipo_fidelidade = serializers.CharField(
        read_only=True)

    class Meta:
        model = Perfil
        fields = ('data_nascimento', 'telemovel', 'estudante', 'qrcode_url',
                  'ultima_atualizacao_data_nascimento', 'tipo_fidelidade'
                  )

    def validate_data_nascimento(self, value):
        perfil_instance = self.context.get('perfil_instance')
        if perfil_instance and perfil_instance.data_nascimento == value:
            return value
        agora = timezone.now()
        print('perfil_instance validate_data_nascimento: ', perfil_instance)

        if perfil_instance:
            ultima_atualizacao = perfil_instance\
                .ultima_atualizacao_data_nascimento
            if ultima_atualizacao:
                periodo_minimo = ultima_atualizacao + \
                    timezone.timedelta(days=182.5)  # Aproximadamente 6 meses
                if agora < periodo_minimo:
                    raise serializers.ValidationError(
                        'Só pode ser alterada de 6 em 6 meses.', value)

        return value

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
            errors['telemovel'] = 'O campo telemovel tem de ter 9 digitos.'

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
    # password = serializers.CharField(write_only=True, required=False)

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
        # Validação dos campos obrigatórios
        if not self.instance:
            for field in [
                    'username', 'email', 'first_name',
                    'last_name', 'password']:
                if field not in data:
                    errors[field] = f'O campo {field} é obrigatório.'
            # Verificar unicidade do username, email, telemovel
            if 'username' in data and User.objects.filter(
                    username=data['username']).exists():
                errors['username'] = 'Este nome de utilizador já está em uso.'
            if 'email' in data and User.objects.filter(
                    email=data['email']).exists():
                errors['email'] = 'Já existe um utilizador com este e-mail.'
        # Validação para atualização de dados
        else:
            # Verificação de campos que podem ser atualizados
            if 'username' in data and data['username'] != self.instance.username:
                errors['username'] = 'Já existe um utilizador com esse username.'
            email = data.get('email')
            if 'email' in data and email == self.instance.email:
                errors['email'] = 'Já existe um utilizador com esse email.'
                try:
                    django_validate_email(email)
                except DjangoValidationError:
                    errors['email'] = 'O email é inválido.'

        password = data.get('password')
        if 'password' in data and len(password) < 8:
            errors['password'] = 'A senha deve conter pelo menos 8 caracteres.'
        print('password: ', password)

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil', None)
        password = validated_data.pop('password', None)

        # Usar o método get para evitar keyerror
        username = validated_data.get('username')
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        print('perfil_data: ', perfil_data)
        print('password: ', password)
        print('username: ', username)
        print('email: ', email)
        print('first_name: ', first_name)
        print('last_name: ', last_name)
        # Verificar se todos os campos obrigatórios estão presentes

        if not all([username, email, first_name, last_name, password]):
            raise serializers.ValidationError(
                'Os campos username, email, first_name, last_name e password são obrigatórios.'
            )

        user = User.objects.create_user(    # type: ignore
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save()
        if perfil_data:
            perfil_data['ultima_atualizacao_data_nascimento'] = timezone.now()
            Perfil.objects.create(usuario=user, **perfil_data)

        return user

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})

        # Atualizar a senha, se estiver presente
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)

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
