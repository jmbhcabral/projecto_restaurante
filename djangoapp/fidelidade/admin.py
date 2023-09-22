from django.contrib import admin
from fidelidade.models import (
    Fidelidade, ProdutoFidelidadeIndividual,
    ComprasFidelidade, OfertasFidelidade)


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


@admin.register(ComprasFidelidade)
class ComprasFidelidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'fidelidade', 'utilizador', 'pontos_adicionados')
    search_fields = ('id', 'fidelidade__nome',
                     'utilizador__username', 'pontos_adicionados')
    list_filter = ('id', 'fidelidade__nome',
                   'utilizador__username', 'pontos_adicionados')
    ordering = ('id', 'fidelidade__nome',
                'utilizador__username', 'pontos_adicionados')


@admin.register(OfertasFidelidade)
class OfertasFidelidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'fidelidade', 'utilizador', 'pontos_gastos')
    search_fields = ('id', 'fidelidade__nome',
                     'utilizador__username', 'pontos_gastos')
    list_filter = ('id', 'fidelidade__nome',
                   'utilizador__username', 'pontos_gastos')
    ordering = ('id', 'fidelidade__nome',
                'utilizador__username', 'pontos_gastos')
