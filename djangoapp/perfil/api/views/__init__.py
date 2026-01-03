""" This module contains the views for the API. """
# djangoapp/perfil/api/views/__init__.py
from djangoapp.perfil.api.views.auth_api import (
    LoginApiView,
    LogoutApiView,
    SignupResendApiView,
    SignupStartApiView,
    SignupVerifyApiView,
)

__all__ = [
    "LoginApiView",
    "LogoutApiView",
    "SignupResendApiView",
    "SignupStartApiView",
    "SignupVerifyApiView",
]