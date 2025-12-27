''' Arquivo de configuração de rotas do projeto '''

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('djangoapp.app_version.urls')),
    path('', include('djangoapp.google_reviews.urls', namespace='google_reviews')),
    path('', include('djangoapp.senhas.urls', namespace='senhas')),
    path('', include('djangoapp.restau.urls')),
    path('', include('djangoapp.perfil.urls')),
    path('', include('djangoapp.fidelidade.urls')),
    path('api/catalog/', include('djangoapp.commerce.api.catalog_urls')),
    path('api/commerce/', include('djangoapp.commerce.api.urls')),
    path('api/commerce/admin/', include('djangoapp.commerce.api.admin_urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

# TODO: Remover
# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
