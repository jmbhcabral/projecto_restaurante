from django.urls import path
from perfil import views
from rest_framework.routers import SimpleRouter

app_name = 'perfil'

users_api_v1 = SimpleRouter()
users_api_v1.register(
    'users/api/v1', views.RegisterUserView, basename='users-api',

)


urlpatterns = [
    path('perfil/', views.Criar.as_view(), name='criar'),
    path('confirmar_email/<uuid:token>/', views.ConfirmarEmail.as_view(),
         name='confirmar_email'),
    path('perfil/reenvio_confirmacao_email/<str:username>/', views.ResendConfirmationEmail.as_view(),
         name='resend_confirmation_email'),
    path('perfil/atualizar/', views.Atualizar.as_view(), name='atualizar'),
    path('perfil/login/', views.Login.as_view(), name='login'),
    path('perfil/logout/', views.Logout.as_view(), name='logout'),
    path('perfil/conta/', views.Conta.as_view(), name='conta'),
    path('perfil/conta/vantagens/',
         views.Vantagens.as_view(), name='vantagens'),
    path('perfil/conta/cartao_cliente/',
         views.CartaoCliente.as_view(), name='cartao_cliente'),
    path('perfil/conta/movimentos/',
         views.MovimentosCliente.as_view(), name='movimentos_cliente'),
    # Reset password
    path('perfil/request_reset_password/',
         views.RequestResetPasswordView.as_view(),
         name='request_reset_password'),
    path('perfil/reset_password/<str:token>/', views.ResetPasswordView.as_view(),
         name='reset_password'),
    # Change password
    path('perfil/change_password/', views.ChangePasswordView.as_view(),
         name='change_password'),
]

urlpatterns += users_api_v1.urls
