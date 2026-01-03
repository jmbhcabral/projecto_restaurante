""" Este módulo contém os serviços para os códigos de verificação do utilizador. """
# djangoapp/perfil/services/codes.py
from __future__ import annotations

import hashlib
import hmac
import random

from django.conf import settings


def generate_verification_code(*, length: int = 6) -> str:
    """
    Generate a numeric verification code as a fixed-length string.
    Example: "004381"
    """
    if length <= 0:
        raise ValueError("length must be > 0")

    max_value = (10**length) - 1
    return f"{random.randint(0, max_value):0{length}d}"


def make_code_digest(*, email: str, purpose: str, code: str) -> str:
    """
    Create an HMAC digest for the verification code.
    Binds code to (email + purpose) to avoid reuse.
    """
    key = settings.SECRET_KEY.encode("utf-8")
    msg = f"{email.lower()}|{purpose}|{code}".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def safe_compare_digest(a: str, b: str) -> bool:
    """Constant-time string comparison."""
    return hmac.compare_digest(a, b)