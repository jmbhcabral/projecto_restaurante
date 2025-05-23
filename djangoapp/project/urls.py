''' Arquivo de configuração de rotas do projeto '''

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('app_version.urls')),
    path('', include('senhas.urls', namespace='senhas')),
    path('', include('restau.urls')),
    path('', include('perfil.urls')),
    path('', include('fidelidade.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

# TODO: Remover
# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
