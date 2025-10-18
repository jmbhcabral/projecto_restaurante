from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import AppVersion


@require_GET
def verificar_versao(request, sistema):
    sistema = sistema.lower()
    if sistema not in ('ios', 'android'):
        return JsonResponse({'error': 'sistema inválido'}, status=400)

    versao = AppVersion.objects.filter(sistema_operativo=sistema).first()
    # Se quiseres mesmo usar .latest():
    # versao = AppVersion.objects.filter(sistema_operativo=sistema).latest()

    if not versao:
        return JsonResponse({'detail': 'sem versões disponíveis'}, status=204, safe=False)

    return JsonResponse({
        'latestVersion': versao.versao,
        'forceUpdate': versao.forcar_update,
        'releasedAt': versao.data_lancamento.isoformat(),
        'os': versao.sistema_operativo,
    })