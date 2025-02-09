from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
from django.utils import timezone

from ..serializers import (
    UserRegistrationSerializer, RequestResetPasswordSerializer,
    ValidateResetCodeSerializer, ResetPasswordSerializer,
    UserConfirmationSerializer, CancelRegistrationSerializer
)
from perfil.models import Perfil
from fidelidade.models import RespostaFidelidade



class RegisterUserApiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Restringe a lista de usuários a apenas aqueles com acesso restrito."""
        if self.action == 'list':
            if self.request.user.groups.filter(name='acesso_restrito').exists():
                return User.objects.all().order_by('id')
            else:
                raise PermissionDenied("Você não tem permissão para listar os usuários.")
        return super().get_queryset()
    

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            temp_user = serializer.save()
            response_data = UserRegistrationSerializer(temp_user, many=False).data
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Atualiza o perfil do usuário autenticado"""
        pk = self.kwargs.get('pk')
        user_instance = get_object_or_404(User, pk=pk)
        perfil_instance = Perfil.objects.filter(usuario=user_instance).first()

        print('📩 Dados recebidos para update:', request.data)

        serializer = UserRegistrationSerializer(
            user_instance,
            data=request.data,
            partial=True,  # Garante que não há necessidade de enviar todos os campos
            context={'perfil_instance': perfil_instance, 'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            # Pega todos os dados do serializer
            response_data = dict(serializer.data)
            
            # Garante que existe a chave 'perfil' no response_data
            if 'perfil' not in response_data:
                response_data['perfil'] = {}
            
            # Recarrega o perfil_instance para pegar o valor atualizado do banco
            if perfil_instance:
                perfil_instance.refresh_from_db()
                response_data['perfil']['ultima_atualizacao_data_nascimento'] = perfil_instance.ultima_atualizacao_data_nascimento
            
            return Response(response_data)
        
        error = serializer.errors
        print('🔴 Erro:', error)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_code_email(self, request):
        """Envia um código de redefinição de senha para o email do usuário"""
        serializer = RequestResetPasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Código de redefinição de senha enviado com sucesso."}, status=status.HTTP_200_OK)
        print('🔴 Erro:', serializer.errors)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_reset_code(self, request):
        """Valida o código de redefinição de senha"""
        serializer = ValidateResetCodeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password_mobile(self, request):
        """Redefine a senha do usuário via mobile"""
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.save(), status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

   
class UserConfirmationApiView(APIView):
    """Confirmação do usuário através do código de verificação"""
    def post(self, request):
        serializer = UserConfirmationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            temp_user = request.session.get('temp_user')
            
            # Criar o usuário
            user = User.objects.create_user(
                username=temp_user['username'],
                email=temp_user['email'],
                password=temp_user['password'],
                first_name=temp_user['first_name'],
                last_name=temp_user['last_name'],
            )

            # Criar o perfil associado
            perfil_data = temp_user['perfil_data']
            estudante_id = perfil_data.pop('estudante', None)
            estudante = None
            if estudante_id:
                estudante = get_object_or_404(RespostaFidelidade, id=estudante_id)

            Perfil.objects.create(
                usuario=user,
                estudante=estudante,
                **perfil_data
            )

            # Limpar a sessão
            del request.session['temp_user']

            return Response(
                {"message": "Usuário e perfil criados com sucesso."}, 
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )




class ValidateResetCodeApiView(APIView):
    """Validação do código de redefinição de senha"""
    def post(self, request):
        serializer = ValidateResetCodeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            validated_data = serializer.validated_data  # Armazena numa variável para evitar acessar diretamente

            if isinstance(validated_data, dict) and "reset_token" in validated_data:
                reset_token = validated_data["reset_token"]
            else:
                reset_token = None  # Garante que não há erro caso não exista a chave

            return Response({
                "reset_token": reset_token
            }, status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordApiView(APIView):
    """Redefinição de senha usando um reset token válido"""
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():

            
            return Response(serializer.save(), status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CancelRegistrationApiView(APIView):
    """Cancela o registo do usuário"""
    def post(self, request):
        serializer = CancelRegistrationSerializer(data=request.data, context={'request': request})
        user_id = request.user.id

        user_instance = get_object_or_404(User, pk=user_id)
        perfil_instance = Perfil.objects.filter(usuario=user_instance).first()

        print('📩 Dados recebidos para update:', request.data)
        if serializer.is_valid():


            return Response(serializer.save(), status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    """Obtém o token CSRF para segurança nas requisições"""

    def get(self, request):
        csrf_token = get_token(request)
        return JsonResponse({"csrfToken": csrf_token})