from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from perfil.models import Perfil
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
from django.utils import timezone
import logging
from django.contrib.auth.hashers import check_password
from utils.generate_reset_password_code import generate_reset_password_code
from utils.email_confirmation import (
    send_confirmation_email, send_reset_password_email
    )
from django.utils.dateformat import format

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
        )
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'perfil')
        exclude = ['password']
        read_only_fields = ['id']


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

    def save(self, **kwargs):
        """
        Sobrescreve o método save do serializer para usar o save do modelo Perfil.
        """
        # Recuperar ou criar uma instância de Perfil
        instance = super().save(**kwargs)

        # Chama o método save do modelo, que contém a lógica necessária
        instance.save()

        return instance
    
    def validate_data_nascimento(self, value):
        """
        Valida a alteração da data de nascimento, respeitando as restrições do modelo.
        """

        perfil_instance = self.context.get('perfil_instance')
        agora = timezone.now()
        
        

        # Se a data não foi alterada, retorna o valor sem validações adicionais
        if perfil_instance and perfil_instance.data_nascimento == value:
            return value

        # Verifica a última alteração e aplica a regra dos 6 meses
        if perfil_instance and perfil_instance.ultima_atualizacao_data_nascimento:
            ultima_atualizacao = perfil_instance.ultima_atualizacao_data_nascimento
            periodo_minimo = ultima_atualizacao + timezone.timedelta(days=182.5)  # Aproximadamente 6 meses
            if agora < periodo_minimo:
                raise serializers.ValidationError(
                    'A data de nascimento só pode ser alterada após 6 meses desde a última alteração.'
                )

        # Caso passe todas as validações, retorna o valor para ser atualizado
        return value

    def validate_telemovel(self, value):
        perfil_instance = self.context.get('perfil_instance')
        # Ignora a validação se estiver atualizando o perfil atual
        if perfil_instance and perfil_instance.telemovel == value:
            return value

        # Verifica se o número de telemóvel já está em uso
        if Perfil.objects.filter(telemovel=value).exclude(
                pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError(
                'Este número de telemóvel já está em uso.'
            )

        return value

    def validate(self, data):
        """
        Validações adicionais a nível de serializer.
        """
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
        # Se o QR code não estiver disponível, retorna None
        if not hasattr(obj, 'qr_code') or not obj.qr_code:
            return None

        request = self.context.get('request')
        qrcode_url = obj.qr_code.url if obj.qr_code else None
        return request.build_absolute_uri(qrcode_url) if qrcode_url else None

    def update(self, instance, validated_data):
        pass


class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        )
    perfil = PerfilSerializer()

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
                raise serializers.ValidationError({
                    'username': ['Este nome de utilizador já está em uso.']
                })
        return value

    def validate_email(self, value):
        # Se estamos criando um novo usuário ou atualizando o e-mail de um
        # existente, verificar unicidade.
        if not self.instance or (self.instance.email != value):
            if get_user_model().objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    ['Já existe um utilizador com este e-mail.']
                )
        return value

    def validate_password(self, value):
        # Se não estiver atualizando um usuário, simplesmente retorne o valor
        if not self.instance:
            return value

        # Se estiver atualizando e a senha for diferente da armazenada
        if self.instance and not check_password(value, self.instance.password):
            # Aqui você pode adicionar validação adicional, como comprimento da senha
            if len(value) < 8:
                raise serializers.ValidationError({
                    'password': ['A senha deve conter pelo menos 8 caracteres.']
                })
            return value

        # Se a senha fornecida for a mesma que a armazenada, ignore a atualização
        raise serializers.SkipField()
    
    

    def validate(self, data):
        errors = {}
        # Validação dos campos obrigatórios
        if not self.instance:  # Criação de novo usuário
            # Verifica campos obrigatórios
            for field in ['username', 'email', 'first_name', 'last_name', 'password']:
                if field not in data:
                    errors[field] = f'O campo {field} é obrigatório.'
            
            # Verifica unicidade apenas se os campos existirem
            if 'username' in data and User.objects.filter(username=data['username']).exists():
                errors['username'] = 'Este nome de utilizador já está em uso.'
            if 'email' in data and User.objects.filter(email=data['email']).exists():
                errors['email'] = 'Já existe um utilizador com este e-mail.'
        
        else:  # Atualização de usuário existente
            # Impedir a alteração do username
            if 'username' in data and data['username'] != self.instance.username:
                errors['username'] = 'O nome de utilizador não pode ser alterado.'
            
            if 'email' in data:
                # Verifica se o email é diferente do atual
                if data['email'] != self.instance.email:
                    # Verifica se existe outro usuário com este email
                    if User.objects.filter(email=data['email']).exists():
                        errors['email'] = 'Já existe um utilizador com esse email.'
                    try:
                        django_validate_email(data['email'])
                    except DjangoValidationError:
                        errors['email'] = 'O email é inválido.'

        # Validação da senha
        if 'password' in data and len(data['password']) < 8:
            errors['password'] = 'A senha deve conter pelo menos 8 caracteres.'

        # Validação do perfil
        perfil_data = data.get('perfil')
        if not self.instance and not perfil_data:  # Só exige perfil na criação
            errors['perfil'] = 'O campo perfil é obrigatório.'
        elif perfil_data and not isinstance(perfil_data, dict):
            errors['perfil'] = 'O campo perfil deve ser um objeto JSON válido.'

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
        code = generate_reset_password_code()

        # Verificar se todos os campos obrigatórios estão presentes
        if not all([username, email, first_name, last_name, password, code]):
            raise serializers.ValidationError(
                'Os campos username, email, first_name, last_name e password são obrigatórios.'
            )
        
        # Converter data_nascimento para string
        if perfil_data and 'data_nascimento' in perfil_data:
            perfil_data['data_nascimento'] = perfil_data['data_nascimento'].isoformat()

        # Certifique-se de que 'estudante' é um ID numérico
        if perfil_data and 'estudante' in perfil_data:
            perfil_data['estudante'] = perfil_data['estudante'].id  # Use o ID do objeto

        temp_user = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'code': code,
            'code_expiration_time': format(timezone.now() + timezone.timedelta(minutes=10), 'U'),
            'perfil_data': perfil_data,
        }

        print('temp_user: ', temp_user)

        request = self.context.get('request')
        if request:
            request.session['temp_user'] = temp_user
        
        send_confirmation_email(request, email, username, code)

        # Retornar o temp_user para fins de serialização
        return temp_user

    def to_representation(self, instance):
        # Modificar a representação para lidar com temp_user
        if isinstance(instance, dict):
            # Se instance for um dict, estamos lidando com temp_user
            perfil_data = instance.pop('perfil_data', {})
            instance['perfil'] = perfil_data
            return instance  # Retorna o dicionário diretamente

        return super().to_representation(instance)

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})

        # Atualizar a senha, se estiver presente
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)

        # Atualizar os dados do utilizador (exceto username)
        for attr, value in validated_data.items():
            if attr != 'username':  # Garantir que username não seja atualizado
                setattr(instance, attr, value)
        instance.save()

        # Atualizar o perfil do utilizador
        perfil_instance = getattr(instance, 'perfil', None)
        if perfil_instance and perfil_data:
            for attr, value in perfil_data.items():
                setattr(perfil_instance, attr, value)
            perfil_instance.save()

        return instance
    

class UserConfirmationSerializer(serializers.Serializer):
    code = serializers.IntegerField()

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("O objeto 'request' não foi encontrado no contexto.")

        # Obter o `temp_user` da sessão
        temp_user = request.session.get('temp_user', None)
        if not temp_user:
            raise serializers.ValidationError("Não foi possível encontrar o utilizador temporário na sessão.")

        # Validar o código de confirmação

        code = request.data.get('code')

        code_expiration_time = temp_user.get('code_expiration_time')

        if str(temp_user.get('code')) != str(code):
            raise serializers.ValidationError("O código de confirmação está incorreto.")

        if timezone.now() > code_expiration_time:
            del request.session['temp_user']
            raise serializers.ValidationError("O código de confirmação expirou.")

        return data

    def save(self):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("O objeto 'request' não foi encontrado no contexto.")

        temp_user = request.session.get('temp_user')

        if not temp_user:
            raise serializers.ValidationError("Não foi possível encontrar o utilizador temporário na sessão.")

        # Criar o utilizador definitivo
        user = User.objects.create_user(
            username=temp_user['username'],
            email=temp_user['email'],
            first_name=temp_user['first_name'],
            last_name=temp_user['last_name'],
            password=temp_user['password'],
            is_active=True  # O utilizador agora está ativado
        )

        # Criar o perfil associado
        perfil_data = temp_user.get('perfil_data', {})
        Perfil.objects.create(usuario=user, **perfil_data)

        # Remover o `temp_user` da sessão
        del request.session['temp_user']

        return user

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


    def validate_email(self, data):
        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError("O objeto 'request' não foi encontrado no contexto.")

        email = request.data.get('email')
        print('email: ', email)

        email = email.strip().lower()

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("Este email não está registado.")
        
        request.session['reset_password_email'] = email

        return data

    def save(self):
        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError("O objeto 'request' não foi encontrado no contexto.")

        email = request.session.get('reset_password_email')

        user = User.objects.filter(email=email).first() 

        if not user:
            raise serializers.ValidationError("Não foi possível encontrar o email na sessão.")
        
        reset_code = generate_reset_password_code()

        user.perfil.reset_password_code = reset_code
        user.perfil.reset_password_code_expires = timezone.now()
        user.perfil.save()

        send_reset_password_email(request, email, reset_code)

        return user
    

class ValidateResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()

    def validate(self, data):
        email = data.get('email').strip().lower()
        code = data.get('code')

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Este email não está registado.")

        perfil = user.perfil
        print('perfil: ', perfil)
        if perfil.reset_password_code != code:
            raise serializers.ValidationError("O código de redefinição de senha está incorreto.")

        expiration_time = perfil.reset_password_code_expires + timezone.timedelta(minutes=15)
        if timezone.now() > expiration_time:
            raise serializers.ValidationError("O código de redefinição de senha expirou.")

        # Adiciona o user ao contexto para reutilização na view, se necessário.
        data['user'] = user
        return data



