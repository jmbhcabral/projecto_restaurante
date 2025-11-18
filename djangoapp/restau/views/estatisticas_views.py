from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import render
from fidelidade.models import MovimentoPontos


@login_required
@user_passes_test(lambda user: user.groups.filter(
    name='acesso_restrito').exists())
def admin_estatisticas(request):
    utilizadores = User.objects.all()
    utilizadores_ativos = User.objects.filter(is_active=True)
    utilizadores_inativos = User.objects.filter(is_active=False)


    total_pontos_ganhos = MovimentoPontos.objects.filter(
        tipo='CREDITO').aggregate(
        total_pontos_ganhos=models.Sum('pontos'))['total_pontos_ganhos'] or 0
    total_pontos_gastos = MovimentoPontos.objects.filter(
        tipo='DEBITO_RES').aggregate(
        total_pontos_gastos=models.Sum('pontos'))['total_pontos_gastos'] or 0
    total_pontos_expirados = MovimentoPontos.objects.filter(
        tipo='DEBITO_EXP').aggregate(
        total_pontos_expirados=models.Sum('pontos'))['total_pontos_expirados'] or 0
    total_compras = MovimentoPontos.objects.filter(tipo='CREDITO').count()
    total_ofertas = MovimentoPontos.objects.filter(tipo='DEBITO_RES').count()
    context = {
        'utilizadores': utilizadores,
        'utilizadores_ativos': utilizadores_ativos,
        'utilizadores_inativos': utilizadores_inativos,
        'total_pontos_ganhos': total_pontos_ganhos,
        'total_pontos_gastos': total_pontos_gastos,
        'total_pontos_expirados': total_pontos_expirados,
        'total_compras': total_compras,
        'total_ofertas': total_ofertas,
    }
    return render(request, 'restau/pages/admin_estatisticas.html', context)