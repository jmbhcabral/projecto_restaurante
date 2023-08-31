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

        self.renderizar = render(self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    pass


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Login')


class Logout(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Logout')
