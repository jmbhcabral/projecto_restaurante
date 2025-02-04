from django.contrib import admin
from perfil.models import (Perfil, Morada, PasswordResetToken)


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
