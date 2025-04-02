from django.contrib import admin

from .models import AppVersion


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('sistema_operativo', 'versao', 'forcar_update', 'data_lancamento')
    list_filter = ('sistema_operativo', 'forcar_update')
    search_fields = ('sistema_operativo', 'versao')
    list_per_page = 10


