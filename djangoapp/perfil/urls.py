from django.urls import path
from perfil.views import views

app_name = 'perfil'

urlpatterns = [
    path('perfil/', views.Criar.as_view(), name='criar'),
    path('perfil/atualizar/', views.Atualizar.as_view(), name='atualizar'),
    path('perfil/login/', views.Login.as_view(), name='login'),
    path('perfil/logout/', views.Logout.as_view(), name='logout'),
    path('perfil/conta/', views.Conta.as_view(), name='conta'),
    path('perfil/conta/vantagens', views.Vantagens.as_view(), name='vantagens'),
]
