from django.urls import path
from . import views

app_name = 'perfil'

urlpatterns = [
    path('perfil/criar', views.Criar.as_view(), name='criar'),
    path('perfil/atualizar/', views.Atualizar.as_view(), name='atualizar'),
    path('perfil/login/', views.Login.as_view(), name='login'),
    path('perfil/logout/', views.Logout.as_view(), name='logout'),
]
