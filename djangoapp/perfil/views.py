from django.contrib import messages
# from typing import Any
# from django import http
from django.shortcuts import render, get_object_or_404, redirect
# from django.views.generic import ListView
from django.views import View
# from django.http import HttpResponse
from . import models
from . import forms
from restau.models import FrontendSetup
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        main_image = FrontendSetup.objects \
            .filter(imagem_topo__isnull=False) \
            .order_by('-id') \
            .first()

        main_logo = FrontendSetup.objects \
            .filter(imagem_logo__isnull=False) \
            .order_by('-id') \
            .first()

        self.perfil = None

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user
            ).first()

            self.context = {
                'main_logo': main_logo,
                'main_image': main_image,
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user,
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
        else:
            self.context = {
                'main_logo': main_logo,
                'main_image': main_image,
                'userform': forms.UserForm(
                    data=self.request.POST or None
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                )
            }

        self.userform = self.context['userform']
        self.perfilform = self.context['perfilform']

        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(self.request, self.template_name,
                                 self.context)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')

        # Usuários logados
        if self.request.user.is_authenticated:
            usuario = get_object_or_404(
                User, username=self.request.user.username)
            print(usuario.username)

            usuario.username = username

            if password:
                usuario.set_password(password)

            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario
                print(self.perfilform.cleaned_data)
                perfil = models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()

            else:
                perfil = self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()

        # Usuários não logados (criação)
        else:
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        if password:
            autentica = authenticate(
                self.request,
                username=usuario,
                password=password
            )

            if autentica:
                login(self.request, user=usuario)

        messages.success(
            self.request,
            'Perfil atualizado com sucesso!')

        return redirect('perfil:conta')
        return self.renderizar


class Atualizar(BasePerfil):
    template_name = 'perfil/atualizar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        main_image = FrontendSetup.objects \
            .filter(imagem_topo__isnull=False) \
            .order_by('-id') \
            .first()

        main_logo = FrontendSetup.objects \
            .filter(imagem_logo__isnull=False) \
            .order_by('-id') \
            .first()

        self.perfil = None

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user
            ).first()

            self.context = {
                'main_logo': main_logo,
                'main_image': main_image,
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user,
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
        else:
            return redirect('perfil:criar')

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.context)


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        if not username or not password:
            messages.error(
                self.request,
                'Usuário ou senha inválidos!'
            )
            return redirect('perfil:criar')

        usuario = authenticate(
            self.request,
            username=username,
            password=password
        )
        if not usuario:
            messages.error(
                self.request,
                'Usuário ou senha inválidos!'
            )
            return redirect('perfil:criar')

        login(self.request, user=usuario)
        messages.success(
            self.request,
            'Login efetuado com sucesso!'
        )
        return redirect('perfil:conta')


class Logout(View):
    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect('restau:index')


class Conta(View):
    template_name = 'perfil/conta.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        main_image = FrontendSetup.objects \
            .filter(imagem_topo__isnull=False) \
            .order_by('-id') \
            .first()

        main_logo = FrontendSetup.objects \
            .filter(imagem_logo__isnull=False) \
            .order_by('-id') \
            .first()

        perfil = models.Perfil.objects.filter(
            usuario=self.request.user
        ).first()

        self.context = {
            'main_logo': main_logo,
            'main_image': main_image,
            'perfil': perfil,
        }

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.context)
