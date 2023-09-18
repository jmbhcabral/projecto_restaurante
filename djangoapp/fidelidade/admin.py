from django.contrib import admin
from fidelidade.models import Fidelidade, ProdutoFidelidadeIndividual


@admin.register(Fidelidade)
class FidelidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'unidade', 'ementa')
    search_fields = ('nome', 'unidade', 'ementa__nome')
    list_filter = ('nome', 'unidade', 'ementa__nome')
    ordering = ('nome', 'unidade', 'ementa__nome')


@admin.register(ProdutoFidelidadeIndividual)
class ProdutoFidelidadeIndividualAdmin(admin.ModelAdmin):
    list_display = ('produto', 'fidelidade',
                    'pontos_recompensa', 'pontos_para_oferta')
    search_fields = ('produto__nome', 'fidelidade__nome',
                     'pontos_recompensa', 'pontos_para_oferta')
    list_filter = ('produto__nome', 'fidelidade__nome',
                   'pontos_recompensa', 'pontos_para_oferta')
    ordering = ('produto__nome', 'fidelidade__nome',
                'pontos_recompensa', 'pontos_para_oferta')
