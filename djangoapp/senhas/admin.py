''' Admin do app senhas '''

from django.contrib import admin

from djangoapp.senhas.models import FrasePub, Senhas


@admin.register(Senhas)
class SenhasAdmin(admin.ModelAdmin):
    ''' Admin do app senhas '''
    list_display = 'id', 'numero', 'created_at'
    list_display_links = 'id', 'numero'
    search_fields = 'id', 'numero', 'created_at'


@admin.register(FrasePub)
class FrasePubAdmin(admin.ModelAdmin):
    ''' Admin do app senhas '''
    list_display = 'id', 'frase', 'escolhida', 'created_at'
    list_display_links = 'id', 'frase'
    search_fields = 'id', 'frase', 'escolhida', 'created_at'
    list_editable = 'escolhida',
