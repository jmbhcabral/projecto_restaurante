''' Função para listar as compras e ofertas de um utilizador '''

from django.utils import timezone

from djangoapp.fidelidade import models as fidelidade_models


def listar_compras_ofertas(user):
    ''' Lista as compras e ofertas de um utilizador '''

    compras_fidelidade = fidelidade_models.ComprasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em')

    ofertas_fidelidade = fidelidade_models.OfertasFidelidade.objects.filter(
        utilizador=user).order_by('-criado_em')

    movimentos = []

    agora = timezone.now()
    for compra in compras_fidelidade:
        criado_em_local = timezone.localtime(compra.criado_em)
        disponivel_amanha = agora.date() <= criado_em_local.date()
        expirado = compra.expirado

        movimentos.append({
            'data': criado_em_local.strftime('%Y-%m-%d'),
            'tipo': 'Compra',
            'valor': compra.compra,
            'pontos': compra.pontos_adicionados,
            'cor': 'orange' if disponivel_amanha else 'black',
            'disponivel_amanha': disponivel_amanha,
            'expirado': expirado,
        })

    for oferta in ofertas_fidelidade:
        processado = oferta.processado
        movimentos.append({
            'data': oferta.criado_em.strftime('%Y-%m-%d'),
            'tipo': 'Oferta',
            'valor': '-----',
            'pontos': '-' + str(oferta.pontos_gastos),
            'cor': 'red',
            'processado': processado,
        })

    # Ordenar os movimentos por data decrescente
    movimentos.sort(key=lambda x: x['data'], reverse=True)

    return movimentos
