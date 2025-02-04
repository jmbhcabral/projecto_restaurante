from django.urls import path
from perfil import views
from rest_framework.routers import SimpleRouter
from .views.perfil_api import (
    UserConfirmationApiView, ValidateResetCodeApiView, ResetPasswordApiView, 
    GetCSRFToken, RegisterUserApiView, CancelRegistrationApiView
    )

app_name = 'perfil'

users_api_v1 = SimpleRouter()
users_api_v1.register(
    'users/api/v1', views.RegisterUserApiView, basename='users-api',
)


urlpatterns = [
    path('perfil/', views.Criar.as_view(), name='criar'),
    path('perfil/user_verification_code/', views.VerificationCodeView.as_view(),
         name='user_verification_code'),
    path('perfil/atualizar/', views.Atualizar.as_view(), name='atualizar'),
    path('perfil/login/', views.Login.as_view(), name='login'),
    path('perfil/logout/', views.Logout.as_view(), name='logout'),
    path('perfil/conta/', views.Conta.as_view(), name='conta'),
    path('perfil/conta/regras/',
         views.Regras.as_view(), name='regras'),
    path('perfil/conta/cartao_cliente/',
         views.CartaoCliente.as_view(), name='cartao_cliente'),
    path('perfil/conta/movimentos/',
         views.MovimentosCliente.as_view(), name='movimentos_cliente'),
    # Reset password
    path('perfil/request_reset_password/',
         views.RequestResetPasswordView.as_view(),
         name='request_reset_password'),
    path('perfil/user_reset_code/',
         views.ResetCodeView.as_view(),
         name='user_reset_code'),
    path('perfil/user_resend_reset_code/',
         views.ResendResetCodeView.as_view(),
         name='user_resend_reset_code'),
    path('perfil/reset_password/', views.ResetPasswordView.as_view(),
         name='reset_password'),
    # Change password
    path('perfil/change_password/', views.ChangePasswordView.as_view(),
         name='change_password'),

    # API
    # User confirmation
    path('perfil/confirmation_api/', UserConfirmationApiView.as_view(), name='user-confirmation-api'),
    path('perfil/validate_reset_code_api/', ValidateResetCodeApiView.as_view(), name='validate-reset-code-api'),
    path('perfil/reset_password_api/', ResetPasswordApiView.as_view(), name='reset-password-api'),
    path('perfil/get_csrf_token/', GetCSRFToken.as_view(), name='get-csrf-token'),
    path('perfil/cancel_registration_api/', CancelRegistrationApiView.as_view(), name='cancel-registration-api'),
]

urlpatterns += users_api_v1.urls
