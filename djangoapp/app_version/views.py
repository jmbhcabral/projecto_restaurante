from django.http import JsonResponse

from .models import AppVersion


def verificar_versao(request, sistema):
    versao = AppVersion.objects.filter(sistema_operativo=sistema).latest('data_lancamento')
    return JsonResponse({
        'versao': versao.versao,
        'forcar_update': versao.forcar_update,
        'data_lancamento': versao.data_lancamento,
    })
