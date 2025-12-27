import logging
from typing import List

from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from djangoapp.fidelidade.models import RespostaFidelidade
from djangoapp.perfil.models import Notification, Perfil, PushNotificationToken
from djangoapp.perfil.serializers import (
    CancelRegistrationSerializer,
    NotificationBroadcastSerializer,
    RequestResetPasswordSerializer,
    ResetPasswordSerializer,
    UserConfirmationSerializer,
    UserRegistrationSerializer,
    ValidateResetCodeSerializer,
)
from djangoapp.utils.notifications import (
    send_push_notification,
    send_push_notifications_to_all,
    send_push_notifications_to_users,
)


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

    
class SavePushTokenView(APIView):
    """
    API para gerir os tokens de notificação push
    """

    def post(self, request):
        """Regista ou atualiza um token de notificação push"""
        token = request.data.get('token')
        user_id = request.data.get('user_id')

        print('📩 Token recebido:', token)
        print('📩 User ID recebido:', user_id)
        print('request.data:', request.data)

        if not token or not user_id:
            return Response(
                {'error': 'Token e User ID são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Busca o token no banco de dados
        obj, created = PushNotificationToken.objects.get_or_create(
            expo_token=token,
            defaults={'user_id': user_id}  # Define o user apenas na criação
        )

        # Se o token já existia mas estava associado a outro user, atualiza
        if not created and obj.user.pk != user_id:
            print(f'🔄 Token já existe, mas pertence ao user {obj.user.pk}. Atualizando para {user_id}.')
            obj.user = User.objects.get(pk=user_id)  # Atribui o objeto User em vez do ID
            obj.save()  # Não esqueça de salvar a alteração

        return Response(
            {'message': 'Token salvo com sucesso'},
            status=status.HTTP_200_OK,
        )
    

logger = logging.getLogger(__name__)


class SendPushNotificationView(APIView):
    """
    Envia uma notificação push para o usuário.
    """

    def post(self, request):
        """
        Envia uma notificação push para o usuário.
        """
        user = request.user
        title = request.data.get('title')
        message = request.data.get('message')
        data = request.data.get('data')

        if not user:
            return Response(
                {'error': 'Usuário não autenticado'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        if not title or not message:
            return Response(
                {'error': 'Título e mensagem são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            response = send_push_notification(user, title, message, data)
            print('📩 Notificação push enviada com sucesso')
            print('📩 Resposta:', response)
            return Response(
                {'message': 'Notificação push enviada com sucesso'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class SendPushNotificationToAllView(APIView):
    """
    Envia uma notificação push para todos os usuários.
    """

    def post(self, request):
        """
        Envia uma notificação push para todos os usuários.
        """
        title = request.data.get('title')
        message = request.data.get('message')
        data = request.data.get('data')

        if not title or not message:
            return Response(
                {'error': 'Título e mensagem são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

        try:
            response = send_push_notifications_to_all(title, message, data)

            print('📩 Notificação push enviada com sucesso')
            print('📩 Resposta:', response)
            return Response(
                {'message': 'Notificação push enviada com sucesso'},
                status=status.HTTP_200_OK,
            )
        


        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class NotificationBroadcastView(APIView):
    """Permite que utilizadores administrativos enviem notificações em massa."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = NotificationBroadcastSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payload = serializer.validated_data
        if not isinstance(payload, dict):
            return Response({"error": "Dados inválidos"}, status=status.HTTP_400_BAD_REQUEST)

        title = payload.get("title", "")
        body = payload.get("body", "")
        data = dict(payload.get("notification_data") or {})
        target = payload["target"]
        user_ids: List[int]

        if target == "all":
            user_ids = list(User.objects.filter(is_active=True).values_list("id", flat=True))
        elif target == "group":
            group_name = payload["group_name"]
            group = Group.objects.filter(name=group_name).first()
            if not group:
                return Response(
                    {"detail": "Grupo não encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            user_ids = list(
                group.user_set.filter(is_active=True).values_list("id", flat=True)
            )
        else:  # target == "user"
            user = None
            if payload.get("user_id"):
                user = User.objects.filter(
                    pk=payload["user_id"], is_active=True
                ).first()
            if not user and payload.get("email"):
                user = User.objects.filter(
                    email=payload["email"], is_active=True
                ).first()
            if not user:
                return Response(
                    {"detail": "Utilizador não encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            user_ids = [user.pk]

        user_ids = list({user_id for user_id in user_ids if user_id})

        if not user_ids:
            return Response(
                {"detail": "Nenhum utilizador encontrado para o target solicitado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notifications = [
            Notification(user_id=user_id, title=title, body=body, data={**data})
            for user_id in user_ids
        ]
        Notification.objects.bulk_create(notifications)

        push_result = send_push_notifications_to_users(user_ids, title, body, data)

        logger.info(
            "Broadcast de notificações concluído por user=%s target=%s recipients=%d push_result=%s",
            request.user.id,
            target,
            len(user_ids),
            push_result,
        )

        response_payload = {
            "created": len(notifications),
            "message": "Notificações enviadas com sucesso.",
        }

        if isinstance(push_result, dict):
            if "error" in push_result:
                response_payload["message"] = "Notificações criadas, mas ocorreu um erro ao enviar push."
                response_payload["push"] = {"error": push_result["error"]}
            else:
                response_payload["push"] = {
                    "sent": push_result.get("sent", 0),
                    "failed": push_result.get("failed", 0),
                }

        return Response(response_payload, status=status.HTTP_201_CREATED)
        
