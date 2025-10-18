from django.contrib import admin

from .models import AppVersion


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('sistema_operativo', 'versao', 'forcar_update', 'data_lancamento')
    list_filter = ('sistema_operativo', 'forcar_update')
    ordering = ('-data_lancamento',)
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # garante validações de clean()
        super().save_model(request, obj, form, change)