from django.shortcuts import render


def configuracao(request):
    # frontend = FrontendSetup.objects \
    #     .select_related(
    #         'frontend_imagem_logo', 'frontend_imagem_topo',
    #         'frontend_intro', 'frontend_frase_inspiradora',
    #         'frontend_frase_cima', 'frontend_frase_baixo') \
    #     .all() \

    context = {
        # 'frontend': frontend,
    }

    return render(
        request,
        'restau/pages/configuracao.html',
        context,
    )
