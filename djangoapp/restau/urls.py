from django.urls import path
from restau import views
from restau.views import (
    MyTokenObtainPairView, MyTokenRefreshView
)
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


# namespace
app_name = 'restau'

produto_api_v1_router = SimpleRouter()
produto_api_v1_router.register(
    'produtos/api/v1',
    views.ProdutosAPIv1ViewSet,  # type: ignore
    basename='produtos-api'
)
# se não tiver outras urls sem ser de api
# urlpatterns = produto_api_v1_router.urls

urlpatterns = [
    path(
        '',
        views.index,  # type: ignore
        name='index'
    ),
    path(
        'restau/pages/encomendas/',
        views.encomendas,  # type: ignore
        name='encomendas'
    ),
    path(
        'restau/pages/admin_home/',
        views.admin_home,  # type: ignore
        name='admin_home'
    ),
    # product
    path(
        'restau/pages/produtos/',
        views.produtos,  # type: ignore
        name='produtos'
    ),
    path(
        'restau/pages/<int:produto_id>/',
        views.produto,  # type: ignore
        name='produto'
    ),
    path(
        'restau/pages/criar_produto/',
        views.criar_produto,  # type: ignore
        name='criar_produto'
    ),
    path(
        'restau/pages/<int:produto_id>/atualizar_produto/',
        views.atualizar_produto,  # type: ignore
        name='atualizar_produto'
    ),
    path(
        'restau/pages/<int:produto_id>/apagar_produto/',
        views.apagar_produto,  # type: ignore
        name='apagar_produto'
    ),
    path(
        'restau/pages/ordenar_produtos/',
        views.ordenar_produtos,  # type: ignore
        name='ordenar_produtos'
    ),
    # category
    path(
        'restau/pages/categorias/',
        views.categorias,  # type: ignore
        name='categorias'
    ),
    path(
        'restau/pages/categoria/<int:categoria_id>/',
        views.categoria,  # type: ignore
        name='categoria'
    ),
    path(
        'restau/pages/criar_categoria/',
        views.criar_categoria,  # type: ignore
        name='criar_categoria'
    ),
    path(
        'restau/pages/<int:categoria_id>/atualizar_categoria/',
        views.atualizar_categoria,  # type: ignore
        name='atualizar_categoria'
    ),
    path(
        'restau/pages/<int:categoria_id>/apagar_categoria/',
        views.apagar_categoria,  # type: ignore
        name='apagar_categoria'
    ),
    path(
        'restau/pages/ordenar_categorias/',
        views.ordenar_categorias,  # type: ignore
        name='ordenar_categorias'
    ),
    # subcategoria
    path(
        'restau/pages/subcategorias/',
        views.Subcategorias,  # type: ignore
        name='subcategorias'
    ),
    path(
        'restau/pages/subcategoria/<int:subcategoria_id>/',
        views.subcategoria,  # type: ignore
        name='subcategoria'
    ),
    path(
        'restau/pages/criar_subcategoria/',
        views.criar_subcategoria,  # type: ignore
        name='criar_subcategoria'),
    path(
        'restau/pages/<int:subcategoria_id>/atualizar_subcategoria/',
        views.atualizar_subcategoria,  # type: ignore
        name='atualizar_subcategoria'
    ),
    path(
        'restau/pages/<int:subcategoria_id>/apagar_subcategoria/',
        views.apagar_subcategoria,  # type: ignore
        name='apagar_subcategoria'
    ),
    path(
        'restau/pages/ordenar_subcategorias/',
        views.ordenar_subcategorias,  # type: ignore
        name='ordenar_subcategorias'
    ),
    # Ementas
    path(
        'restau/pages/criar_ementa/',
        views.criar_ementa,  # type: ignore
        name='criar_ementa'
    ),
    path(
        'restau/pages/<int:ementa_id>/atualizar_ementa/',
        views.atualizar_ementa,  # type: ignore
        name='atualizar_ementa'
    ),
    path(
        'restau/pages/<int:ementa_id>/apagar_ementa/',
        views.apagar_ementa,  # type: ignore
        name='apagar_ementa'
    ),
    path(
        'restau/pages/ementa/<int:ementa_id>/',
        views.ementa,  # type: ignore
        name='ementa'
    ),
    path(
        'restau/pages/ementas/',
        views.ementas,  # type: ignore
        name='ementas'
    ),
    path(
        'restau/pages/povoar_ementa/<int:ementa_id>/',
        views.povoar_ementa,  # type: ignore
        name='povoar_ementa'
    ),
    # Configuração
    path(
        'restau/pages/configuracao/',
        views.configuracao,  # type: ignore
        name='configuracao'
    ),
    # Galeria
    path(
        'restau/pages/galeria/',
        views.galeria,  # type: ignore
        name='galeria'
    ),
    path(
        'restau/pages/adicionar_foto/',
        views.adicionar_foto,  # type: ignore
        name='adicionar_foto'
    ),
    path(
        'restau/pages/povoar_galeria/',
        views.povoar_galeria,  # type: ignore
        name='povoar_galeria'
    ),
    # ImagemLogo
    path(
        'restau/pages/logos/',
        views.imagem_logo,  # type: ignore
        name='imagem_logo'
    ),
    path(
        'restau/pages/criar_logo/',
        views.criar_logo,  # type: ignore
        name='criar_logo'
    ),
    path(
        'restau/pages/apagar_logo/',
        views.apagar_logo,  # type: ignore
        name='apagar_logo'
    ),
    path(
        'restau/pages/escolher_logo/',
        views.escolher_logo,  # type: ignore
        name='escolher_logo'
    ),
    # ImagemTopo
    path(
        'restau/pages/imagem_topo/',
        views.imagem_topo,  # type: ignore
        name='imagem_topo'
    ),
    path(
        'restau/pages/criar_imagem_topo/',
        views.criar_imagem_topo,  # type: ignore
        name='criar_imagem_topo'
    ),
    path(
        'restau/pages/apagar_imagem_topo/',
        views.apagar_imagem_topo,  # type: ignore
        name='apagar_imagem_topo'
    ),
    path(
        'restau/pages/escolher_imagem_topo/',
        views.escolher_imagem_topo,  # type: ignore
        name='escolher_imagem_topo'
    ),
    # Intro
    path(
        'restau/pages/intro/',
        views.intro,  # type: ignore
        name='intro'
    ),
    path(
        'restau/pages/criar_intro/',
        views.criar_intro,  # type: ignore
        name='criar_intro'
    ),
    path(
        'restau/pages/apagar_intro/',
        views.apagar_intro,  # type: ignore
        name='apagar_intro'
    ),
    path(
        'restau/pages/escolher_intro/',
        views.escolher_intro,  # type: ignore
        name='escolher_intro'
    ),
    # Intro Imagem
    path(
        'restau/pages/intro_imagem/',
        views.intro_imagem,  # type: ignore
        name='intro_imagem'
    ),
    path(
        'restau/pages/criar_intro_imagem/',
        views.criar_intro_imagem,  # type: ignore
        name='criar_intro_imagem'
    ),
    path(
        'restau/pages/apagar_intro_imagem/',
        views.apagar_intro_imagem,  # type: ignore
        name='apagar_intro_imagem'
    ),
    path(
        'restau/pages/escolher_intro_imagem/',
        views.escolher_intro_imagem,  # type: ignore
        name='escolher_intro_imagem'
    ),
    # Frase Cima
    path(
        'restau/pages/frase_cima/',
        views.frase_cima,  # type: ignore
        name='frase_cima'
    ),
    path(
        'restau/pages/criar_frase_cima/',
        views.criar_frase_cima,  # type: ignore
        name='criar_frase_cima'
    ),
    path(
        'restau/pages/apagar_frase_cima/',
        views.apagar_frase_cima,  # type: ignore
        name='apagar_frase_cima'
    ),
    path(
        'restau/pages/escolher_frase_cima/',
        views.escolher_frase_cima,  # type: ignore
        name='escolher_frase_cima'
    ),
    # Imagem Frase Cima
    path(
        'restau/pages/imagem_frase_cima/',
        views.imagem_frase_cima,  # type: ignore
        name='imagem_frase_cima'
    ),
    path(
        'restau/pages/criar_imagem_frase_cima/',
        views.criar_imagem_frase_cima,  # type: ignore
        name='criar_imagem_frase_cima'
    ),
    path(
        'restau/pages/apagar_imagem_frase_cima/',
        views.apagar_imagem_frase_cima,  # type: ignore
        name='apagar_imagem_frase_cima'
    ),
    path(
        'restau/pages/escolher_imagem_frase_cima/',
        views.escolher_imagem_frase_cima,  # type: ignore
        name='escolher_imagem_frase_cima'
    ),
    # Imagem Frase Central
    path(
        'restau/pages/frase_central/',
        views.frase_central,  # type: ignore
        name='frase_central'
    ),
    path(
        'restau/pages/criar_frase_central/',
        views.criar_frase_central,  # type: ignore
        name='criar_frase_central'
    ),
    path(
        'restau/pages/apagar_frase_central/',
        views.apagar_frase_central,  # type: ignore
        name='apagar_frase_central'
    ),
    path(
        'restau/pages/escolher_frase_central/',
        views.escolher_frase_central,  # type: ignore
        name='escolher_frase_central'
    ),
    # Frase baixo
    path(
        'restau/pages/frase_baixo/',
        views.frase_baixo,  # type: ignore
        name='frase_baixo'
    ),
    path(
        'restau/pages/criar_frase_baixo/',
        views.criar_frase_baixo,  # type: ignore
        name='criar_frase_baixo'
    ),
    path(
        'restau/pages/apagar_frase_baixo/',
        views.apagar_frase_baixo,  # type: ignore
        name='apagar_frase_baixo'
    ),
    path(
        'restau/pages/escolher_frase_baixo/',
        views.escolher_frase_baixo,  # type: ignore
        name='escolher_frase_baixo'
    ),
    # Imagem Frase baixo
    path(
        'restau/pages/imagem_frase_baixo/',
        views.imagem_frase_baixo,  # type: ignore
        name='imagem_frase_baixo'
    ),
    path(
        'restau/pages/criar_imagem_frase_baixo/',
        views.criar_imagem_frase_baixo,  # type: ignore
        name='criar_imagem_frase_baixo'
    ),
    path(
        'restau/pages/apagar_imagem_frase_baixo/',
        views.apagar_imagem_frase_baixo,  # type: ignore
        name='apagar_imagem_frase_baixo'
    ),
    path(
        'restau/pages/escolher_imagem_frase_baixo/',
        views.escolher_imagem_frase_baixo,  # type: ignore
        name='escolher_imagem_frase_baixo'
    ),
    # Imagem Padrao
    path(
        'restau/pages/imagem_padrao/',
        views.imagem_padrao,  # type: ignore
        name='imagem_padrao'
    ),
    path(
        'restau/pages/criar_imagem_padrao/',
        views.criar_imagem_padrao,  # type: ignore
        name='criar_imagem_padrao'
    ),
    path(
        'restau/pages/apagar_imagem_padrao/',
        views.apagar_imagem_padrao,  # type: ignore
        name='apagar_imagem_padrao'
    ),
    path(
        'restau/pages/escolher_imagem_padrao/',
        views.escolher_imagem_padrao,  # type: ignore
        name='escolher_imagem_padrao'
    ),
    # Contatos Site
    path(
        'restau/pages/contatos_site/',
        views.contatos_site,  # type: ignore
        name='contatos_site'
    ),
    path(
        'restau/pages/criar_contatos_site/',
        views.criar_contatos_site,  # type: ignore
        name='criar_contatos_site'
    ),
    path(
        'restau/pages/editar_contatos_site/<int:contato_id>',
        views.editar_contatos_site,  # type: ignore
        name='editar_contatos_site'
    ),
    # Google Maps
    path(
        'restau/pages/google_maps/',
        views.google_maps,  # type: ignore
        name='google_maps'
    ),
    path(
        'restau/pages/criar_google_maps/',
        views.criar_google_maps,  # type: ignore
        name='criar_google_maps'
    ),
    path(
        'restau/pages/editar_google_maps/<int:map_id>',
        views.editar_google_maps,  # type: ignore
        name='editar_google_maps'
    ),
    # Horário
    path(
        'restau/pages/horario/',
        views.horario,  # type: ignore
        name='horario'
    ),
    path(
        'restau/pages/criar_horario/',
        views.criar_horario,  # type: ignore
        name='criar_horario'
    ),
    path(
        'restau/pages/editar_horario/<int:horario_id>',
        views.editar_horario,  # type: ignore
        name='editar_horario'
    ),
    # Admin-Utilizadores
    path(
        'restau/pages/admin_utilizadores/',
        views.admin_utilizadores,  # type: ignore
        name='admin_utilizadores'
    ),
    path(
        'restau/pages/admin_utilizador/<int:utilizador_pk>/',
        views.admin_utilizador,  # type: ignore
        name='admin_utilizador'
    ),
    path(
        'restau/pages/compras_utilizador/<int:utilizador_id>/',
        views.compras_utilizador,  # type: ignore
        name='compras_utilizador'
    ),
    path(
        'restau/pages/ofertas_utilizador/<int:utilizador_id>/',
        views.ofertas_utilizador,  # type: ignore
        name='ofertas_utilizador'
    ),
    path(
        'restau/pages/movimentos/<int:utilizador_id>/',
        views.movimentos,  # type: ignore
        name='movimentos'),

    # Produtos API
    # path(
    #     'produtos/api/v1/',
    #     views.ProdutosAPIv1ViewSet.as_view(  # type: ignore
    #         {
    #             'get': 'list',
    #             'post': 'create'
    #         }
    #     ),
    #     name='produtos_api_v1'
    # ),
    # path(
    #     'produtos/api/v1/<int:pk>/',
    #     views.ProdutosAPIv1ViewSet.as_view(  # type: ignore
    #         {
    #             'get': 'retrieve',
    #             'patch': 'partial_update',
    #             'delete': 'destroy',
    #         }
    #     ),

    #     name='detalhe_produtos_api_v1'
    # ),
    path(
        'produtos/api/v1/categoria/<int:pk>/',
        views.categoria_api_detalhe,  # type: ignore
        name='produto_categoria_api_v1'
    ),
    path(
        'produtos/api/v1/subcategoria/<int:pk>/',
        views.subcategoria_api_detalhe,  # type: ignore
        name='produto_subcategoria_api_v1'
    ),
    path(
        'api/token/',
        MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        MyTokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'api/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'
    ),
]

urlpatterns += produto_api_v1_router.urls
