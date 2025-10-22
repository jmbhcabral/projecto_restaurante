import logging
from typing import List

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group, User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from utils.notifications import send_push_notifications_to_users

from perfil.models import Notification
from perfil.serializers import NotificationBroadcastSerializer

logger = logging.getLogger(__name__)


@staff_member_required
def send_notification_to_all_view(request, *args, **kwargs):
    """Endpoint legado descontinuado em favor de NotificationBroadcastView."""
    raise Http404("Este endpoint de envio de notificações foi descontinuado.")


@method_decorator(staff_member_required, name='dispatch')
class NotificationBroadcastAdminView(View):
    """View para enviar notificações broadcast através da administração do Django."""
    
    def get(self, request):
        """Exibe o formulário de broadcast de notificações."""
        # Buscar grupos disponíveis
        groups = Group.objects.all().order_by('name')
        
        context = {
            'title': 'Enviar Notificação Broadcast',
            'groups': groups,
            'has_permission': True,
        }
        return render(request, 'admin/perfil/notification_broadcast.html', context)
    
    def post(self, request):
        """Processa o envio da notificação broadcast."""
        # Preparar dados do formulário
        notification_data_raw = request.POST.get('notification_data', '{}').strip()
        
        # Se o campo estiver vazio ou for apenas {}, usar dict vazio
        if not notification_data_raw or notification_data_raw == '{}':
            notification_data = {}
        else:
            notification_data = notification_data_raw
            
        form_data = {
            'title': request.POST.get('title', '').strip(),
            'body': request.POST.get('body', '').strip(),
            'target': request.POST.get('target', 'all'),
            'group_name': request.POST.get('group_name', ''),
            'user_id': request.POST.get('user_id', ''),
            'email': request.POST.get('email', '').strip(),
            'notification_data': notification_data,
        }
        
        # Limpar campos vazios
        if not form_data['user_id']:
            form_data.pop('user_id', None)
        if not form_data['group_name']:
            form_data.pop('group_name', None)
        if not form_data['email']:
            form_data.pop('email', None)
        
        # Validar dados com o serializer
        serializer = NotificationBroadcastSerializer(data=form_data)
        
        if not serializer.is_valid():
            # Exibir erros de validação
            if isinstance(serializer.errors, dict):
                for field, errors in serializer.errors.items():
                    if isinstance(errors, list):
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                    else:
                        messages.error(request, f"{field}: {errors}")
            else:
                # Se não for um dict, exibir erro genérico
                messages.error(request, f"Erro de validação: {serializer.errors}")
            
            # Buscar grupos para o contexto
            groups = Group.objects.all().order_by('name')
            context = {
                'title': 'Enviar Notificação Broadcast',
                'groups': groups,
                'has_permission': True,
                'form_data': form_data,
            }
            return render(request, 'admin/perfil/notification_broadcast.html', context)
        
        # Processar o broadcast
        try:
            payload = serializer.validated_data
            if not isinstance(payload, dict):
                messages.error(request, "Dados inválidos recebidos.")
                return self._render_form_with_error(request, form_data)
                
            title = payload.get("title", "")
            body = payload.get("body", "")
            data = dict(payload.get("notification_data") or {})
            target = payload.get("target", "all")
            user_ids: List[int]

            if target == "all":
                user_ids = list(User.objects.filter(is_active=True).values_list("id", flat=True))
            elif target == "group":
                group_name = payload.get("group_name")
                if not group_name:
                    messages.error(request, "Nome do grupo é obrigatório.")
                    return self._render_form_with_error(request, form_data)
                group = Group.objects.filter(name=group_name).first()
                if not group:
                    messages.error(request, "Grupo não encontrado.")
                    return self._render_form_with_error(request, form_data)
                user_ids = list(
                    group.user_set.filter(is_active=True).values_list("id", flat=True)
                )
            else:  # target == "user"
                user = None
                user_id = payload.get("user_id")
                email = payload.get("email")
                
                if user_id:
                    user = User.objects.filter(
                        pk=user_id, is_active=True
                    ).first()
                if not user and email:
                    user = User.objects.filter(
                        email=email, is_active=True
                    ).first()
                if not user:
                    messages.error(request, "Utilizador não encontrado.")
                    return self._render_form_with_error(request, form_data)
                user_ids = [user.pk]

            user_ids = list({user_id for user_id in user_ids if user_id})

            if not user_ids:
                messages.error(request, "Nenhum utilizador encontrado para o target solicitado.")
                return self._render_form_with_error(request, form_data)

            # Criar notificações no banco de dados
            notifications = [
                Notification(user_id=user_id, title=title, body=body, data={**data})
                for user_id in user_ids
            ]
            Notification.objects.bulk_create(notifications)

            # Enviar push notifications
            push_result = send_push_notifications_to_users(user_ids, title, body, data)

            # Log da operação
            logger.info(
                "Broadcast de notificações concluído por user=%s target=%s recipients=%d push_result=%s",
                request.user.id,
                target,
                len(user_ids),
                push_result,
            )

            # Mensagem de sucesso
            success_message = f"Notificações enviadas com sucesso para {len(notifications)} utilizador(es)."
            
            if isinstance(push_result, dict):
                if "error" in push_result:
                    success_message += f" Notificações criadas, mas ocorreu um erro ao enviar push: {push_result['error']}"
                else:
                    sent = push_result.get("sent", 0)
                    failed = push_result.get("failed", 0)
                    success_message += f" Push notifications: {sent} enviadas, {failed} falharam."
            
            messages.success(request, success_message)
            
            # Redirecionar para a mesma página (limpar formulário)
            return HttpResponseRedirect(reverse('perfil:notification_broadcast_admin'))
            
        except Exception as e:
            logger.exception("Erro ao enviar broadcast de notificações: %s", e)
            messages.error(request, f"Erro ao enviar notificações: {str(e)}")
            return self._render_form_with_error(request, form_data)
    
    def _render_form_with_error(self, request, form_data):
        """Renderiza o formulário com dados preenchidos em caso de erro."""
        groups = Group.objects.all().order_by('name')
        context = {
            'title': 'Enviar Notificação Broadcast',
            'groups': groups,
            'has_permission': True,
            'form_data': form_data,
        }
        return render(request, 'admin/perfil/notification_broadcast.html', context)


