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
    list_display = ('id', 'produto', 'fidelidade',
                    'pontos_recompensa', 'pontos_para_oferta')
    search_fields = ('id', 'produto__nome', 'fidelidade__nome',
                     'pontos_recompensa', 'pontos_para_oferta')
    list_filter = ('id', 'produto__nome', 'fidelidade__nome',
                   'pontos_recompensa', 'pontos_para_oferta')
    ordering = ('id', 'produto__nome', 'fidelidade__nome',
                'pontos_recompensa', 'pontos_para_oferta')
