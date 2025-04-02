from django.urls import path

from app_version import views

app_name = 'app_version'

urlpatterns = [
    path('verificar-versao/<str:sistema>/', views.verificar_versao, name='verificar_versao'),
]
