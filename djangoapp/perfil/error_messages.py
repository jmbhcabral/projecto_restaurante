""" Este módulo contém as mensagens de erro para o aplicativo de perfil. """
# djangoapp/perfil/error_messages.py
from __future__ import annotations

from typing import Final, Mapping

from djangoapp.perfil.errors import ErrorCode

ERROR_MESSAGES_PT: Final[Mapping[str, str]] = {
    # Verification codes
    ErrorCode.CODE_NOT_FOUND: "Não existe nenhum código ativo. Pede um novo código.",
    ErrorCode.CODE_INVALIDATED: "Este código já não é válido. Utiliza o código mais recente ou pede um novo.",
    ErrorCode.CODE_EXPIRED: "Este código expirou. Pede um novo código.",
    ErrorCode.CODE_INCORRECT: "Código incorreto.",
    ErrorCode.CODE_MAX_ATTEMPTS: "Atingiste o limite de tentativas. Pede um novo código.",
    ErrorCode.CODE_MAX_RESENDS: "Atingiste o limite de reenvios. Tenta mais tarde.",

    # Rate limiting (domain)
    ErrorCode.RATE_LIMITED: "Demasiadas tentativas. Tenta novamente mais tarde.",

    # Auth
    ErrorCode.AUTH_USER_EXISTS: "Já existe uma conta com este email.",
    ErrorCode.AUTH_USER_NOT_FOUND: "Conta não encontrada.",
    ErrorCode.AUTH_ALREADY_ACTIVE: "Esta conta já está ativa. Faz login.",
    ErrorCode.AUTH_DISABLED: "Conta desativada.",
    ErrorCode.AUTH_INVALID_CREDENTIALS: "Credenciais inválidas.",
    
    # Signup flow (temp_user)
    ErrorCode.AUTH_SIGNUP_NOT_STARTED: "O registo ainda não foi iniciado. Faz o registo novamente.",
    ErrorCode.AUTH_SIGNUP_SESSION_EXPIRED: "A sessão de registo expirou. Faz o registo novamente.",
}

def get_error_message(code: str) -> str:
    # fallback avoids KeyError if a code is missing
    return ERROR_MESSAGES_PT.get(code, "Ocorreu um erro. Tenta novamente.")