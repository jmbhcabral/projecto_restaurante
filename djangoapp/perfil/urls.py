# djangoapp/perfil/urls.py
from __future__ import annotations

from typing import List, Union

from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from djangoapp.perfil import views
from djangoapp.perfil.api.views import (
    LoginApiView,
    LoginJwtApiView,
    LogoutApiView,
    SignupResendApiView,
    SignupStartApiView,
    SignupVerifyApiView,
)
from djangoapp.perfil.api.views.password_reset import (
    PasswordResetResendApiView,
    PasswordResetStartApiView,
    PasswordResetVerifyApiView,
)
from djangoapp.perfil.views.admin_views import NotificationBroadcastAdminView
from djangoapp.perfil.views.perfil_api import (
    CancelRegistrationApiView,
    GetCSRFToken,
    NotificationBroadcastView,
    ResetPasswordApiView,
    SavePushTokenView,
    SendPushNotificationToAllView,
    SendPushNotificationView,
    UserConfirmationApiView,
    ValidateResetCodeApiView,
)

app_name = 'perfil'

users_api_v1 = SimpleRouter()
users_api_v1.register(
    'users/api/v1', views.RegisterUserApiView, basename='users-api',
)


urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path('perfil/', views.Criar.as_view(), name='criar'),
    path('perfil/user_verification_code/', views.VerificationCodeView.as_view(),
         name='user_verification_code'),
    path('perfil/atualizar/', views.Atualizar.as_view(), name='atualizar'),
    path('perfil/login/', views.Login.as_view(), name='login'),
    path('perfil/logout/', views.Logout.as_view(), name='logout'),
    path('perfil/conta/', views.Conta.as_view(), name='conta'),
    path('perfil/conta/cancelar/', views.CancelarConta.as_view(), name='cancelar_conta'),
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
    path('perfil/save_push_token/', SavePushTokenView.as_view(), name='save-push-token'),
    path('perfil/send_push_notification/', SendPushNotificationView.as_view(), name='send-push-notification'),
    path('perfil/send_push_notification_to_all/', SendPushNotificationToAllView.as_view(), name='send-push-notification-to-all'),
    path('perfil/notifications/broadcast/', NotificationBroadcastView.as_view(), name='notification-broadcast'),
    
    # Admin URLs
    path('admin/perfil/notification-broadcast/', NotificationBroadcastAdminView.as_view(), name='notification_broadcast_admin'),

    # New Auth flow
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("signup/verify/", views.SignUpVerificationCodeView.as_view(), name="signup_verify"),
    path("signup/resend/", views.SignUpResendCodeView.as_view(), name="signup_resend"),
    path("login/", views.LoginView.as_view(), name="login_v2"),
    path("perfil/onboarding/", views.OnboardingView.as_view(), name="onboarding"),

        # New Auth API
    path("api/auth/signup/start/", SignupStartApiView.as_view(), name="api_signup_start"),
    path("api/auth/signup/verify/", SignupVerifyApiView.as_view(), name="api_signup_verify"),
    path("api/auth/signup/resend/", SignupResendApiView.as_view(), name="api_signup_resend"),
    path("api/auth/login/", LoginApiView.as_view(), name="api_login"),
    path("api/auth/logout/", LogoutApiView.as_view(), name="api_logout"),
    path("api/auth/password/reset/start/", PasswordResetStartApiView.as_view(), name="api_password_reset_start"),
    path("api/auth/password/reset/verify/", PasswordResetVerifyApiView.as_view(), name="api_password_reset_verify"),
    path("api/auth/password/reset/resend/", PasswordResetResendApiView.as_view(), name="api_password_reset_resend"),

    # JWT API
    path("api/auth/login/jwt/", LoginJwtApiView.as_view(), name="api_login_jwt"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
]


urlpatterns += users_api_v1.urls
