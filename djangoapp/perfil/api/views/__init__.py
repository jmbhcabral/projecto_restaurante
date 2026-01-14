""" This module contains the views for the API. """
# djangoapp/perfil/api/views/__init__.py
from djangoapp.perfil.api.views.auth_api import (
    LoginApiView,
    LogoutApiView,
    SignupResendApiView,
    SignupStartApiView,
    SignupVerifyApiView,
)
from djangoapp.perfil.api.views.auth_jwt import LoginJwtApiView, LogoutJwtApiView
from djangoapp.perfil.api.views.me import MeApiView
from djangoapp.perfil.api.views.onboarding_optional import (
    OnboardingOptionalCompleteApiView,
)
from djangoapp.perfil.api.views.ping import PingApiView

__all__ = [
    "LoginApiView",
    "LogoutApiView",
    "SignupResendApiView",
    "SignupStartApiView",
    "SignupVerifyApiView",
    "LoginJwtApiView",
    "LogoutJwtApiView",
    "MeApiView",
    "PingApiView",
    "OnboardingOptionalCompleteApiView",
]