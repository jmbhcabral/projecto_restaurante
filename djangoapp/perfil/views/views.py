from django.contrib import messages
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from perfil import models as perfil_models
from perfil import forms as perfil_forms
from fidelidade import models as fidelidade_models
from fidelidade import forms as fidelidade_forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from restau.models import ActiveSetup


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        self.perfil = None

        if self.request.user.is_authenticated:
            self.perfil = perfil_models.Perfil.objects.filter(
                usuario=self.request.user
            ).first()

            self.context = {
                'active_setup': active_setup,
                'userform': perfil_forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user,
                ),
                'perfilform': perfil_forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
        else:
            self.context = {
                'active_setup': active_setup,
                'userform': perfil_forms.UserForm(
                    data=self.request.POST or None
                ),
                'perfilform': perfil_forms.PerfilForm(
                    data=self.request.POST or None,
                )
            }

        self.userform = self.context['userform']
        self.perfilform = self.context['perfilform']

        # if self.request.user.is_authenticated:
        #     self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(self.request, self.template_name,
                                 self.context)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            return self.renderizar

        password = self.userform.cleaned_data.get('password')

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
            'Conta criada com sucesso!')

        return redirect('perfil:conta')


@method_decorator(login_required, name='dispatch')
class Atualizar(BasePerfil):
    template_name = 'perfil/atualizar.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)

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
                perfil = perfil_models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()

            else:
                perfil = self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()

        else:
            messages.error(
                self.request,
                'Não foi possivel atualizar o perfil!'
            )
            return redirect('perfil:criar')

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
            'Conta atualizada com sucesso!')

        return redirect('perfil:conta')


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


@method_decorator(login_required, name='dispatch')
class Logout(View):
    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect('restau:index')


# @method_decorator(login_required, name='dispatch')
class Conta(BasePerfil):
    template_name = 'perfil/conta.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        total_recompensas = fidelidade_models.ComprasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_pontos_ganhos=models.Sum('pontos_adicionados'))

        total_ofertas = fidelidade_models.OfertasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_pontos_gastos=models.Sum('pontos_gastos'))

        total_recompensas_decimal = (
            total_recompensas['total_pontos_ganhos'] or 0)
        total_ofertas_decimal = total_ofertas['total_pontos_gastos'] or 0

        total_pontos = total_recompensas_decimal - total_ofertas_decimal

        self.context = {
            'total_pontos': total_pontos,
            'total_recompensas': total_recompensas_decimal,
            'total_ofertas': total_ofertas_decimal,
        }

        return render(self.request, self.template_name, self.context)


# class Deletar(View):
#     def get(self, *args, **kwargs):
#         if not self.request.user.is_authenticated:
#             return redirect('perfil:criar')

#         usuario = get_object_or_404(
#             User, username=self.request.user.username)

#         usuario.delete()

#         messages.success(
#             self.request,
#             'Conta deletada com sucesso!'
#         )
#         return redirect('restau:index')


class CartaoCliente(View):
    template_name = 'perfil/cartao_cliente.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        # user = self.request.user

        # if not user.is_authenticated:
        #     return redirect('perfil:criar')

        # perfil = user.perfil
        # tipo_fidelidade = perfil.tipo_fidelidade

        # lista_fidelidade = ProdutoFidelidadeIndividual.objects \
        #     .filter(fidelidade=tipo_fidelidade) \
        #     .select_related('produto') \
        #     .order_by(
        #         'produto__categoria', 'produto__subcategoria', 'produto__ordem'
        #     )

        # self.context = {
        #     'main_logo': main_logo,
        #     'main_image': main_image,
        #     'lista_fidelidade': lista_fidelidade,
        # }
        perfil = perfil_models.Perfil.objects.filter(
            usuario=self.request.user).first()

        self.context = {
            'active_setup': active_setup,
            'perfil': perfil,
        }

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)


class Vantagens(View):
    template_name = 'perfil/vantagens.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        user = self.request.user

        if not user.is_authenticated:
            return redirect('perfil:criar')

        perfil = user.perfil
        tipo_fidelidade = perfil.tipo_fidelidade

        lista_fidelidade = fidelidade_models.ProdutoFidelidadeIndividual\
            .objects \
            .filter(fidelidade=tipo_fidelidade) \
            .select_related('produto') \
            .order_by(
                'produto__categoria', 'produto__subcategoria', 'produto__ordem'
            )

        self.context = {
            'active_setup': active_setup,
            'lista_fidelidade': lista_fidelidade,
        }

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)
