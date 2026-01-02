# djangoapp/perfil/views/views_auth.py
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from djangoapp.perfil.forms_auth import LoginForm, RegisterForm
from djangoapp.perfil.models import Perfil
from djangoapp.perfil.services import perfil_service
from djangoapp.restau.models import ActiveSetup
from djangoapp.utils.email_confirmation import send_confirmation_email
from djangoapp.utils.generate_reset_password_code import generate_reset_password_code

User = get_user_model()

logger = logging.getLogger(__name__)

class SignUpView(View):
    """
    Page with 2 columns:
    - Login (POSTs to login_v2)
    - Signup (POSTs here)
    """

    template_name = "perfil/signup.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("perfil:conta")

        active_setup = ActiveSetup.objects.order_by("-id").first()

        context = {
            "active_setup": active_setup,
            "signup_form": RegisterForm(),
            "login_form": LoginForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("perfil:conta")

        request.session.pop("temp_user", None)

        signup_form = RegisterForm(request.POST)
        if not signup_form.is_valid():
            for errors in signup_form.errors.values():
                for e in errors:
                    messages.error(request, str(e))
            return redirect("perfil:signup")

        email = signup_form.cleaned_data["email"]
        password = signup_form.cleaned_data["password1"]
        username = email  # new users: username=email

        code = generate_reset_password_code()

        request.session["temp_user"] = {
            "username": username,
            "email": email,
            "password": password,
            "code": code,
            "resend_count": 0,
            "last_sent_at": timezone.now().isoformat(),
        }

        send_confirmation_email(request, email, code)
        messages.success(request, "Verifique o seu email para criar a conta!")
        return redirect("perfil:signup_verify")


class SignUpVerificationCodeView(View):
    template_name = "perfil/signup_verification_code.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("perfil:conta")

        temp_user = request.session.get("temp_user")
        if not temp_user:
            messages.error(request, "Sessão de registo expirada. Tente novamente.")
            return redirect("perfil:signup")

        context = {
            "email": temp_user.get("email", ""),
            "resend_count": temp_user.get("resend_count", 0),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("perfil:conta")

        temp_user = request.session.get("temp_user")
        if not temp_user or "code" not in temp_user:
            messages.error(request, "Sessão de registo expirada. Tente novamente.")
            return redirect("perfil:signup")

        # Keep template context stable on errors
        context = {
            "email": temp_user.get("email", ""),
            "resend_count": temp_user.get("resend_count", 0),
        }

        # 1) Read code inputs
        code_1 = (request.POST.get("code_1") or "").strip()
        code_2 = (request.POST.get("code_2") or "").strip()
        code_3 = (request.POST.get("code_3") or "").strip()

        # 2) Validate presence
        if not all([code_1, code_2, code_3]):
            messages.error(request, "Código incompleto! Preencha todos os campos.")
            return render(request, self.template_name, context)

        # 3) Validate numeric and build final code
        try:
            final_code = int(f"{code_1}{code_2}{code_3}")
        except ValueError:
            messages.error(request, "Código inválido! Insira apenas números.")
            return render(request, self.template_name, context)

        # 4) Validate code
        if str(temp_user["code"]) != str(final_code):
            messages.error(request, "Código inválido! Por favor, insira o código correto.")
            return render(request, self.template_name, context)

        # 5) Extract user data
        email = temp_user.get("email", "").strip()
        username = temp_user.get("username", "").strip()
        password = temp_user.get("password", "")

        if not email or not username or not password:
            messages.error(request, "Sessão inválida. Tente novamente.")
            request.session.pop("temp_user", None)
            return redirect("perfil:signup")

        # 6) Guard: email already exists
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Este email já existe. Faça login.")
            request.session.pop("temp_user", None)
            return redirect("perfil:signup")

        # 7) Create user + profile atomically
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )

                perfil = Perfil.objects.create(usuario=user)

                # Ensure business invariants (customer number, derived flags, etc.)
                perfil_service.ensure_perfil_business_defaults(perfil)

        except Exception:
            logger.exception(
                "Error creating user/profile during new signup verification flow",
                extra={"email": email, "username": username},
            )
            messages.error(request, "Ocorreu um erro inesperado. Por favor, tente novamente.")
            return redirect("perfil:signup")

        # 8) Success
        request.session.pop("temp_user", None)
        messages.success(request, "Conta criada com sucesso! completa onboarding para ganhar pontos extra!")
        return redirect("perfil:conta")

class SignUpResendCodeView(View):
    """
    Reenvia o código de verificação do registo (fluxo novo).
    Proteções:
    - cooldown (ex: 60s)
    - max reenvios (ex: 5)
    """

    COOLDOWN_SECONDS = 60
    MAX_RESENDS = 5

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("perfil:conta")

        temp_user = request.session.get("temp_user")
        if not temp_user:
            messages.error(request, "Sessão de registo expirada. Tente novamente.")
            return redirect("perfil:signup")

        email = (temp_user.get("email") or "").strip().lower()

        # Se entretanto o email já existe, cortamos o fluxo
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Este email já existe. Faça login.")
            request.session.pop("temp_user", None)
            return redirect("perfil:signup")

        resend_count = int(temp_user.get("resend_count") or 0)
        if resend_count >= self.MAX_RESENDS:
            messages.error(request, "Atingiu o limite de reenvios. Inicie o registo novamente.")
            request.session.pop("temp_user", None)
            return redirect("perfil:signup")

        # Cooldown
        last_sent_at_raw = temp_user.get("last_sent_at")
        if last_sent_at_raw:
            try:
                last_sent_at = datetime.fromisoformat(last_sent_at_raw)
                if timezone.is_naive(last_sent_at):
                    last_sent_at = timezone.make_aware(last_sent_at, timezone.get_current_timezone())
            except Exception:
                last_sent_at = None
        else:
            last_sent_at = None

        if last_sent_at:
            if timezone.now() < (last_sent_at + timedelta(seconds=self.COOLDOWN_SECONDS)):
                remaining = int(((last_sent_at + timedelta(seconds=self.COOLDOWN_SECONDS)) - timezone.now()).total_seconds())
                messages.warning(request, f"Aguarde {remaining}s antes de pedir novo código.")
                return redirect("perfil:signup_verify")

        # Gerar novo código + guardar
        new_code = generate_reset_password_code()
        temp_user["code"] = new_code
        temp_user["resend_count"] = resend_count + 1
        temp_user["last_sent_at"] = timezone.now().isoformat()

        request.session["temp_user"] = temp_user
        request.session.modified = True

        # Reenviar email
        send_confirmation_email(request, email, new_code)

        messages.success(request, "Novo código enviado para o seu email.")
        return redirect("perfil:signup_verify")

class LoginView(View):
    def get(self, request, *args, **kwargs):
        return redirect("perfil:signup")

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("perfil:conta")

        form = LoginForm(request.POST)
        if not form.is_valid():
            for errors in form.errors.values():
                for e in errors:
                    messages.error(request, str(e))
            return redirect("perfil:signup")

        identifier = (form.cleaned_data["identifier"] or "").strip()
        password = form.cleaned_data["password"]

        user = authenticate(request, username=identifier, password=password)

        if not user:
            messages.error(request, "Credenciais inválidas.")
            return redirect("perfil:signup")

        login(request, user)
        messages.success(request, "Login efetuado com sucesso!")
        return redirect("perfil:conta")

@method_decorator(login_required, name="dispatch")
class OnboardingView(View):
    template_name = "perfil/onboarding.html"

    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, {})