from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('restau.urls')),
    path('', include('perfil.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

# TODO: Remover
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
