from django.contrib import admin
from django.urls import reverse

from djangoapp.perfil.models import (
    Morada,
    Notification,
    PasswordResetToken,
    Perfil,
    PushNotificationToken,
)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_cliente', 'usuario', 'tipo_fidelidade',
                    'data_nascimento', 'telemovel', 'nif', 'estudante',
                    'ultima_actividade')
    list_display_links = 'id', 'numero_cliente', 'usuario'
    search_fields = ('id', 'numero_cliente', 'usuario__username',
                     'usuario__email', 'data_nascimento', 'telemovel', 'nif',
                     'ultima_actividade')


@admin.register(Morada)
class MoradaAdmin(admin.ModelAdmin):
    list_display = 'id', 'usuario', 'finalidade_morada', 'morada', \
        'numero', 'codigo_postal', 'ext_codigo_postal'
    list_display_links = 'id', 'usuario'
    search_fields = 'id', 'usuario', 'finalidade_morada', 'morada', \
        'numero', 'codigo_postal', 'ext_codigo_postal'

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'token', 'created_at'
    list_display_links = 'id', 'user'
    search_fields = 'id', 'user', 'token', 'created_at'


@admin.register(PushNotificationToken)
class PushNotificationTokenAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'expo_token', 'created_at'
    list_display_links = 'id', 'user'
    search_fields = 'id', 'user', 'expo_token', 'created_at'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'read_at')
    list_display_links = ('id', 'user', 'title')
    search_fields = ('title', 'body', 'user__username', 'user__email')
    list_filter = ('created_at', 'read_at')
    
    def changelist_view(self, request, extra_context=None):
        """Adiciona um link para o broadcast de notificações na página de listagem."""
        extra_context = extra_context or {}
        extra_context['broadcast_url'] = reverse('perfil:notification_broadcast_admin')
        return super().changelist_view(request, extra_context=extra_context)


