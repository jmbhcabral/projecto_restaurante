from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..serializers import (
    UserRegistrationSerializer, RequestResetPasswordSerializer,
    ValidateResetCodeSerializer
    )
from rest_framework.pagination import PageNumberPagination
from ..permissions import IsAcessoRestrito, IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from perfil.models import Perfil
from django.http import JsonResponse
from rest_framework.views import APIView
from fidelidade.models import RespostaFidelidade
from rest_framework.decorators import action
from django.utils import timezone


class UsersAPIv1Pagination(PageNumberPagination):
    page_size = 20


class RegisterUserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    pagination_class = UsersAPIv1Pagination
    permission_classes = [IsAcessoRestrito, IsOwner]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        # Restringir a lista de usuários para apenas aqueles que estão
        # ao grupo de acesso restrito.
        if self.action == 'list':
            if self.request.user.groups.filter(name='acesso_restrito').exists():
                return User.objects.all().order_by('id')
            else:
                raise PermissionDenied(
                    "Você não tem permissão para listar os usuários."
                )
        return super().get_queryset()

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def get_permissions(self):
        # Se a ação for 'create', ou seja, registro de novo usuário,
        # permitir que qualquer pessoa acesse a API.
        if self.action == 'create':
            return [AllowAny()]

        # Se a ação for 'list', ou seja, listagem de usuários,
        # permitir que apenas usuários autenticados e que pertençam
        # ao grupo de acesso restrito acessem a API.
        elif self.action == 'list':
            return [IsAcessoRestrito()]

        # Somente o dono do usuário pode alterar ou excluir o registro.
        elif self.action in ['retrieve', 'partial_update', 'destroy']:
            return [IsOwner()]

        else:
            # Caso contrário, retornar as permissões padrão.
            permission_classes = self.permission_classes

        # Retorna instancias das classes de permissão
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(
            data=request.data, context={'request': request}
            )
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user_instance = get_object_or_404(User, pk=pk)
        perfil_instance = Perfil.objects.filter(
            usuario=user_instance).first()

        # Passando a instância para o serializador
        serializer = UserRegistrationSerializer(
            user_instance,
            data=request.data,
            partial=True,
            context={
                'perfil_instance': perfil_instance,
                'request': request,
            }
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_code_email(self, request):
        serializer = RequestResetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Código de redefinição de senha enviado com sucesso.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_reset_code(self, request):
        serializer = ValidateResetCodeSerializer(data=request.data, context={'request': request})
        email = request.data.get('email', '').strip().lower()
        code = request.data.get('code', '')

        if not email or not code:
            return Response(
                {'error': 'O email e o código são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'Este email não está registado.'}, status=404)

        perfil = user.perfil
        print('perfil.reset_password_code: ', perfil.reset_password_code)
        print('code: ', code)

        if perfil.reset_password_code != code:
            return Response({'error': 'Código de verificação inválido.'}, status=400)
        
        expiration_time = user.perfil.reset_password_code_expires + \
            timezone.timedelta(minutes=15)
        
        if timezone.now() > expiration_time:
            return Response({'error': 'O código de verificação expirou.'}, status=400)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Código validado com sucesso.'}, status=200)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password_mobile(self, request):
        email = request.data.get('email', '').strip().lower()
        new_password = request.data.get('new_password', '').strip()

        if not email or not new_password:
            return Response(
                {'error': 'O email e a nova senha são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response('Este email não está registado.', status=404)

        perfil = user.perfil

        # Redefinir a senha do utilizador
        user.set_password(new_password)
        user.save()

        # Limpar o código de redefinição para evitar reutilização
        perfil.reset_password_code = None
        perfil.reset_password_code_expires = None
        perfil.save()

        return Response({'message': 'Senha redefinida com sucesso.'}, status=200)


class UserConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        # Recuperar o temp_user da sessão
        temp_user = request.session.get('temp_user')
        if not temp_user:
            return JsonResponse({'error': 'Usuário temporário não encontrado.'}, status=400)

        # Verificar o código de confirmação
        code = request.data.get('code')
        if not code:
            return JsonResponse({'error': 'Código de confirmação não fornecido.'}, status=400)

        if str(temp_user['code']) != str(code):
            return JsonResponse({'error': 'Código de confirmação inválido.'}, status=400)

        # Criar o usuário
        user = User.objects.create_user(
            username=temp_user['username'],
            email=temp_user['email'],
            password=temp_user['password'],
            first_name=temp_user['first_name'],
            last_name=temp_user['last_name'],
        )

        # Criar o perfil associado
        perfil_data = temp_user['perfil']
        estudante_id = perfil_data.pop('estudante', None)
        estudante = get_object_or_404(RespostaFidelidade, id=estudante_id) if estudante_id else None

        Perfil.objects.create(
            usuario=user,
            estudante=estudante,
            **perfil_data
        )

        # Limpar a sessão
        del request.session['temp_user']

        return JsonResponse({'message': 'Usuário e perfil criados com sucesso.'}, status=201)
    
class ValidateResetCodeView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'O email é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        print('user: ', user)
        print('user.id: ', user.id)
        if not user:
            return Response({'error': 'Este email não está registado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ValidateResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Código validado com sucesso.',
                             'id': user.id,
                             'email': user.email
                             }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

