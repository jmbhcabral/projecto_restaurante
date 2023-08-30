from django.contrib import admin
from perfil.models import Perfil, Morada


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = 'id', 'usuario', 'data_nascimento', 'telemovel', 'nif'
    list_display_links = 'id', 'usuario'
    search_fields = 'id', 'usuario', 'data_nascimento', 'telemovel', 'nif'


@admin.register(Morada)
class MoradaAdmin(admin.ModelAdmin):
    list_display = 'id', 'usuario', 'finalidade_morada', 'morada', \
        'numero', 'codigo_postal', 'ext_codigo_postal'
    list_display_links = 'id', 'usuario'
    search_fields = 'id', 'usuario', 'finalidade_morada', 'morada', \
        'numero', 'codigo_postal', 'ext_codigo_postal'
