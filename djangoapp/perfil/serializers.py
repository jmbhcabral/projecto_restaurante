from typing import Dict, Any
from collections import OrderedDict
from django.contrib.auth import get_user_model
from rest_framework import serializers
from perfil.models import Perfil, PasswordResetToken, RespostaFidelidade
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from utils.generate_reset_password_code import generate_reset_password_code
from utils.email_confirmation import send_confirmation_email, send_reset_password_email
from django.utils.dateformat import format

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'perfil')
        extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True}}


class PerfilSerializer(serializers.ModelSerializer):
    qrcode_url = serializers.SerializerMethodField()
    ultima_atualizacao_data_nascimento = serializers.DateTimeField(read_only=True)
    tipo_fidelidade = serializers.CharField(read_only=True)
    estudante = serializers.PrimaryKeyRelatedField(
        queryset=RespostaFidelidade.objects.all(), required=False  # Torna opcional no update
    )

    class Meta:
        model = Perfil
        fields = ('data_nascimento', 'telemovel', 'estudante', 'qrcode_url', 'ultima_atualizacao_data_nascimento', 'tipo_fidelidade')

    def validate_data_nascimento(self, value):
        """Valida a alteração da data de nascimento respeitando a regra dos 6 meses."""
        perfil_instance = self.context.get('perfil_instance')
        if perfil_instance and perfil_instance.data_nascimento == value:
            return value

        if perfil_instance and perfil_instance.ultima_atualizacao_data_nascimento:
            periodo_minimo = perfil_instance.ultima_atualizacao_data_nascimento + timezone.timedelta(days=182.5)
            if timezone.now() < periodo_minimo:
                raise serializers.ValidationError("A data de nascimento só pode ser alterada após 6 meses.")

        return value

    def validate_telemovel(self, value):
        """Valida se o número de telemóvel já está em uso, apenas se for alterado."""
        perfil_instance = self.context.get('perfil_instance')

        if perfil_instance and perfil_instance.telemovel == value:
            return value  # Não validar se o número for o mesmo

        if Perfil.objects.filter(telemovel=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Este número de telemóvel já está em uso.")

        if len(value) != 9:
            raise serializers.ValidationError("O número de telemóvel deve ter 9 dígitos.")
        
        if not value.isdigit():
            raise serializers.ValidationError("O número de telemóvel deve conter apenas dígitos.")
        
        return value
    
    def validate(self, data):
        """ Impõe a obrigatoriedade de estudante apenas na criação. """
        if self.instance is None and 'estudante' not in data:
            raise serializers.ValidationError({"estudante": "Este campo é obrigatório."})

        return data
    

    def get_qrcode_url(self, obj):
        """Gera a URL do QR code apenas se o perfil já foi criado."""
        if not isinstance(obj, Perfil):  # Se não for uma instância de Perfil, retorna None
            return None

        if not obj.qr_code:  # Se o qrcode ainda não foi gerado, retorna None
            return None

        request = self.context.get('request')
        return request.build_absolute_uri(obj.qr_code.url) if request else obj.qr_code.url
    
    def to_representation(self, instance):
        """Permite a serialização correta quando ainda não há um objeto Perfil real."""
        if isinstance(instance, dict) or isinstance(instance, OrderedDict):
            instance.pop("qrcode_url", None)  # Remove antes de tentar serializar
            return instance

        return super().to_representation(instance)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    perfil = PerfilSerializer()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'perfil', 'id')

    def validate_username(self, value):
        user_instance = self.instance
        if user_instance and user_instance.username == value:
            return value  # Não validar se o username não foi alterado

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de utilizador já está em uso.")
        if len(value) < 3 or len(value) > 30 or ' ' in value:
            raise serializers.ValidationError("O nome de utilizador deve ter entre 3 e 30 caracteres e não pode conter espaços.")
        return value

    def validate_email(self, value):
        user_instance = self.instance
        if user_instance and user_instance.email == value:
            return value  # Não validar se o email não foi alterado

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Já existe um utilizador com este e-mail.")
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("O e-mail fornecido não é válido.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve conter pelo menos 8 caracteres.")
        if " " in value:
            raise serializers.ValidationError("A senha não pode conter espaços.")
        return value
    
    def validate_first_name(self, value):
        if len(value) < 3 or len(value) > 30 or ' ' in value:
            raise serializers.ValidationError("O nome deve ter entre 3 e 30 caracteres e não pode conter espaços.")
        
        if " " in value:
            raise serializers.ValidationError("O nome não pode conter espaços.")
        
        return value
    
    def validate_last_name(self, value):
        if len(value) < 3 or len(value) > 30 or ' ' in value:
            raise serializers.ValidationError("O sobrenome deve ter entre 3 e 30 caracteres e não pode conter espaços.")
        
        if " " in value:
            raise serializers.ValidationError("O sobrenome não pode conter espaços.")
        
        return value


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
        
        print('🔎 perfil_data:', perfil_data)

        # Converter data_nascimento para string
        if perfil_data and 'data_nascimento' in perfil_data:
            perfil_data['data_nascimento'] = perfil_data['data_nascimento'].isoformat()

        if perfil_data:
            perfil_data.pop("qrcode_url", None)  # Remove `qrcode` para evitar erro

        # Certifica-te de que 'estudante' é um ID numérico antes de armazenar
        if perfil_data and 'estudante' in perfil_data:
            estudante = perfil_data['estudante']
            
            if isinstance(estudante, RespostaFidelidade):
                perfil_data['estudante'] = estudante.id  # Converte para inteiro
            elif isinstance(estudante, int):
                pass  # Já é um ID, não precisa fazer nada
            else:
                raise serializers.ValidationError({'perfil.estudante': 'O estudante deve ser um ID válido.'})

            
        
        class TempUser:
            def __init__(self, username, email, first_name, last_name, password, code, perfil_data):
                self.username = username
                self.email = email
                self.first_name = first_name
                self.last_name = last_name
                self.password = password
                self.code = code
                self.code_expiration_time = (timezone.now() + timezone.timedelta(minutes=2)).timestamp()
                self.perfil = perfil_data

        temp_user = TempUser(username, email, first_name, last_name, password, code, perfil_data)

        request = self.context.get('request')
        if request:
            request.session['temp_user'] = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': password,
                'code': code,
                'code_expiration_time': temp_user.code_expiration_time,
                'perfil_data': perfil_data,
            }
            print('🔎 request.session:', request.session['temp_user'])

        send_confirmation_email(request, email, username, code)

        return temp_user

    def to_representation(self, instance):
        """ Permite a serialização correta para dicionários """
        if isinstance(instance, dict):
            instance['perfil'] = instance.get('perfil', {}) or {}  # Garante que perfil existe
            return instance

        return super().to_representation(instance)
    
    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})
        print('🔎 Perfil data:', perfil_data)

        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

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
        
        if not request or not hasattr(request, "session"):
            raise serializers.ValidationError({
                "error": "Erro interno: requisição inválida."
            })

        temp_user = request.session.get('temp_user')
        if not temp_user:
            raise serializers.ValidationError({
                "error": "Não foi possível encontrar o utilizador temporário na sessão."
            })
        
        code = temp_user.get('code')
        if not code:
            raise serializers.ValidationError({
                "error": "Não foi possível encontrar o código de confirmação na sessão."
            })

        if str(code) != str(data.get('code')):
            raise serializers.ValidationError({
                "error": "O código de confirmação está incorreto."
            })
        
        expiration_time = temp_user.get('code_expiration_time')
        if timezone.now().timestamp() > float(expiration_time):
            del request.session['temp_user']
            raise serializers.ValidationError({
                "error": "O código de confirmação expirou. Solicite um novo código."
            })

        return data


class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value.strip().lower()).first()
        if not user:
            raise serializers.ValidationError("Este email não está registado.")
        
        return value
    
    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.get(email=email)
        perfil = getattr(user, 'perfil', None)

        if not perfil:
            raise serializers.ValidationError("Perfil não encontrado para este utilizador.")

        # Gerar código de 6 dígitos
        reset_code = generate_reset_password_code()
        
        # Definir expiração para 15 minutos no futuro
        expiration = timezone.now() + timezone.timedelta(minutes=2)

        # Salvar código e expiração no perfil
        try:
            perfil.reset_password_code = reset_code
            perfil.reset_password_code_expires = expiration
            perfil.save()
        except Exception as e:
            print(f"Erro ao salvar o código de redefinição de senha: {e}")
            raise serializers.ValidationError(f"Surgiu um erro. Por favor, tente novamente mais tarde.")


        # Enviar email com o código
        try:
            send_reset_password_email(email, reset_code)
        except Exception as e:
            print(f"Erro ao enviar o email com o código de redefinição de senha: {e}")
            raise serializers.ValidationError(f"Surgiu um erro. Por favor, tente novamente mais tarde.")



        return {'message': 'Código de redefinição enviado com sucesso.'}


class ValidateResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()

    def validate(self, data):
        user = User.objects.filter(email=data['email'].strip().lower()).first()
        if not user:
            raise serializers.ValidationError("Este email não está registado.")

        perfil = getattr(user, 'perfil', None)
        if not perfil or perfil.reset_password_code != data['code']:
            raise serializers.ValidationError("O código de redefinição de senha está incorreto.")

        agora = timezone.now()
        criacao_reset_token = perfil.reset_password_code_expires
        if agora > criacao_reset_token:
            raise serializers.ValidationError("O código de redefinição de senha expirou. Peça um novo código.")
        
        # Apagar os tokens de redefinição de senha do utilizador anteriores
        PasswordResetToken.objects.filter(user=user).delete()

        # Criar um novo token de redefinição de senha
        reset_token = PasswordResetToken.objects.create(user=user)

        data['reset_token'] = reset_token.token
        return data


class ResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Valida o token e a nova senha antes de redefinir."""
        token = attrs.get("reset_token")
        new_password = attrs.get("new_password", "")

        # Verifica se o token é válido
        token_obj = PasswordResetToken.objects.filter(token=token).first()
        if not token_obj:
            raise serializers.ValidationError("O token é inválido ou já foi utilizado.")

        if token_obj.is_expired():
            raise serializers.ValidationError("O token expirou. Solicite um novo código.")

        # Valida a senha
        if len(new_password) < 8:
            raise serializers.ValidationError("A nova senha deve ter pelo menos 8 caracteres.")
        if " " in new_password:
            raise serializers.ValidationError("A nova senha não pode conter espaços.")

        return attrs

    def save(self, **kwargs):
        """Redefine a senha do utilizador e remove o token."""
        if not isinstance(self.validated_data, dict):
            raise serializers.ValidationError("Erro interno: os dados não foram validados corretamente.")

        token = self.validated_data.get("reset_token")
        new_password = self.validated_data.get("new_password")

        # Busca o token validado
        token_obj = PasswordResetToken.objects.filter(token=token).first()
        if not token_obj:
            raise serializers.ValidationError("O token é inválido ou já foi utilizado.")

        # Atualiza a senha do utilizador
        user = token_obj.user
        user.set_password(new_password)
        user.save()

        # Apaga o token após uso
        token_obj.delete()

        return {"message": "Senha redefinida com sucesso."}
    

class CancelRegistrationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Utilizador não autenticado.")
        
        if request.user.id != value:
            raise serializers.ValidationError("Não tem permissão para cancelar o registo deste utilizador.")
        
        return value

    def save(self, **kwargs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Utilizador não autenticado.")
        
        user = request.user
        if user:
            user_id = user.id
            
            # Atualiza os dados do usuário existente
            user.username = f'{user_id}-Cancelado'
            user.email = f'{user_id}-cancelado@extremeway.pt'
            user.first_name = f'{user_id}-Cancelado'
            user.last_name = f'{user_id}-Cancelado'
            user.set_password(f'{user_id:09d}')  # Garante 9 dígitos
            user.is_active = False
            
            # Atualiza o perfil
            if hasattr(user, 'perfil'):
                user.perfil.telemovel = f'{user_id:09d}'  # Garante 9 dígitos
                user.perfil.data_cancelamento = timezone.now()
                user.perfil.save()
            

            user.save()
            return {"message": "Utilizador cancelado com sucesso."}
        else:
            return {"message": "Utilizador não encontrado."}


