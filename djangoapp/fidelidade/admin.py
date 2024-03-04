from django.contrib import admin
from fidelidade.models import (
    Fidelidade, ProdutoFidelidadeIndividual,
    ComprasFidelidade, OfertasFidelidade, Perguntas, Respostas,
    RespostaFidelidade
)


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
        'id', 'fidelidade', 'utilizador', 'compra', 'pontos_adicionados',
        'criado_em'
    )
    search_fields = ('id', 'fidelidade__nome', 'utilizador__username',
                     'compra', 'pontos_adicionados', 'criado_em'
                     )
    list_filter = ('id', 'fidelidade__nome', 'utilizador__username', 'compra',
                   'pontos_adicionados', 'criado_em'
                   )
    ordering = ('id', 'fidelidade__nome', 'utilizador__username', 'compra',
                'pontos_adicionados', 'criado_em'
                )


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


@admin.register(Perguntas)
class PerguntasAdmin(admin.ModelAdmin):
    list_display = ('id', 'pergunta')
    search_fields = ('id', 'pergunta')
    list_filter = ('id', 'pergunta')
    ordering = ('id', 'pergunta')


@admin.register(Respostas)
class RespostasAdmin(admin.ModelAdmin):
    list_display = ('id', 'pergunta', 'resposta')
    search_fields = ('id', 'pergunta__pergunta', 'resposta')
    list_filter = ('id', 'pergunta__pergunta', 'resposta')
    ordering = ('id', 'pergunta__pergunta', 'resposta')


@admin.register(RespostaFidelidade)
class RespostaFidelidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'resposta', 'tipo_fidelidade')
    search_fields = ('id', 'resposta__resposta', 'tipo_fidelidade__nome')
    list_filter = ('id', 'resposta__resposta', 'tipo_fidelidade__nome')
    ordering = ('id', 'resposta__resposta', 'tipo_fidelidade__nome')
