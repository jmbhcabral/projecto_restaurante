from django.contrib import admin
from perfil.models import (Perfil, Morada, EmailConfirmationToken,
                           PasswordResetToken)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_cliente', 'usuario', 'tipo_fidelidade',
                    'data_nascimento', 'telemovel', 'nif', 'estudante',
                    'ultima_actividade')
    list_display_links = 'id', 'numero_cliente', 'usuario'
    search_fields = ('id', 'numero_cliente', 'usuario', 'tipo_fidelidade',
                     'data_nascimento', 'telemovel', 'nif', 'estudante',
                     'ultima_actividade')


@admin.register(Morada)
class MoradaAdmin(admin.ModelAdmin):
    list_display = 'id', 'usuario', 'finalidade_morada', 'morada', \
        'numero', 'codigo_postal', 'ext_codigo_postal'
    list_display_links = 'id', 'usuario'
    search_fields = 'id', 'usuario', 'finalidade_morada', 'morada', \
        'numero', 'codigo_postal', 'ext_codigo_postal'


@admin.register(EmailConfirmationToken)
class EmailConfirmationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'token')
    list_display_links = ('user', 'created_at', 'token')
    search_fields = ('user', 'created_at', 'token')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'token', 'used')
    list_display_links = ('user', 'created_at', 'token', 'used')
    search_fields = ('user', 'created_at', 'token', 'used')
