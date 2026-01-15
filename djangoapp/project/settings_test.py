# djangoapp/project/settings_test.py
from __future__ import annotations

from .settings import *  # noqa

# English comment: fast, isolated DB for tests (no Docker dependency)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# English comment: speed up hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# English comment: optional - reduce noise and speed up
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# English comment: if you use migrations heavily and want speed, keep default for now.
# You can later disable migrations, but only after everything is stable.