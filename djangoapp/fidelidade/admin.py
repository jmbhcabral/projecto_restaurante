from django.contrib import admin
from fidelidade.models import (
    Fidelidade, ProdutoFidelidadeIndividual,
    ComprasFidelidade, OfertasFidelidade)


@admin.register(Fidelidade)
class FidelidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'desconto', 'ementa')
    search_fields = ('nome', 'desconto', 'ementa__nome')
    list_filter = ('nome', 'desconto', 'ementa__nome')
    ordering = ('nome', 'desconto', 'ementa__nome')


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
    list_display = (
        'id', 'fidelidade', 'utilizador', 'pontos_adicionados', 'criado_em')
    search_fields = ('id', 'fidelidade__nome',
                     'utilizador__username', 'pontos_adicionados', 'criado_em')
    list_filter = ('id', 'fidelidade__nome',
                   'utilizador__username', 'pontos_adicionados', 'criado_em')
    ordering = ('id', 'fidelidade__nome',
                'utilizador__username', 'pontos_adicionados', 'criado_em')


@admin.register(OfertasFidelidade)
class OfertasFidelidadeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fidelidade', 'utilizador', 'pontos_gastos', 'criado_em')
    search_fields = ('id', 'fidelidade__nome',
                     'utilizador__username', 'pontos_gastos', 'criado_em')
    list_filter = ('id', 'fidelidade__nome',
                   'utilizador__username', 'pontos_gastos', 'criado_em')
    ordering = ('id', 'fidelidade__nome',
                'utilizador__username', 'pontos_gastos', 'criado_em')
