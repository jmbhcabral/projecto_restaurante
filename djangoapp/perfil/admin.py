from django.contrib import admin
from django.utils.html import format_html

from perfil.models import (
    Morada,
    NotificationAll,
    NotificationAllSent,
    NotificationUser,
    NotificationUserSent,
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


@admin.register(NotificationAll)
class NotificationAllAdmin(admin.ModelAdmin):
    list_display = ('title', 'message', 'created_at', 'send_now')

    def send_now(self, obj):
        """Botão para criar um registo de envio e disparar a notificação"""
        return format_html(
            '<a class="button" href="/admin/send_notification_all/{}/">📩 Enviar</a>',
            obj.id
        )
    send_now.short_description = "Enviar Notificação"


@admin.register(NotificationAllSent)
class NotificationAllSentAdmin(admin.ModelAdmin):
    list_display = ('notification', 'sent_at', 'status')

@admin.register(NotificationUser)
class NotificationUserAdmin(admin.ModelAdmin):
    list_display = ('title', 'message', 'created_at')

@admin.register(NotificationUserSent)
class NotificationUserSentAdmin(admin.ModelAdmin):
    list_display = ('notification', 'user', 'sent_at', 'status')


