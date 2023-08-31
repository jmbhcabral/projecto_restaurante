from typing import Any
from django import http
from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse
from . import models, forms
from restau.models import FrontendSetup


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
                    instance=self.request.user
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
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

        self.renderizar = render(self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')

        # Usuários logados
        if self.request.user.is_authenticated:
            usuario = self.request.user

        # Usuários não logados (criação)
        else:
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        return self.renderizar


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Login')


class Logout(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Logout')
