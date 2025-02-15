from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect

from perfil.models import NotificationAll, NotificationAllSent


@staff_member_required
def send_notification_to_all_view(request, notification_id):
    """Cria um registo de envio para disparar a notificação"""
    notification = get_object_or_404(NotificationAll, id=notification_id)
    NotificationAllSent.objects.create(notification=notification)

    messages.success(request, "Notificação enviada para todos os utilizadores!")
    return redirect('/admin/perfil/notificationallsent/')



