from django.urls import path
from perfil import views
from rest_framework.routers import SimpleRouter

app_name = 'perfil'

register_user_api_v1 = SimpleRouter()
register_user_api_v1.register(
    'register/api/v1', views.RegisterUserView, basename='register-api',

)

urlpatterns = [
    path('perfil/', views.Criar.as_view(), name='criar'),
    path('perfil/atualizar/', views.Atualizar.as_view(), name='atualizar'),
    path('perfil/login/', views.Login.as_view(), name='login'),
    path('perfil/logout/', views.Logout.as_view(), name='logout'),
    path('perfil/conta/', views.Conta.as_view(), name='conta'),
    path('perfil/conta/vantagens/',
         views.Vantagens.as_view(), name='vantagens'),
    path('perfil/conta/cartao_cliente/',
         views.CartaoCliente.as_view(), name='cartao_cliente'),
]

urlpatterns += register_user_api_v1.urls
