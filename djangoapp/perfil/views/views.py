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
from utils.email_confirmation import send_confirmation_email
from perfil.models import EmailConfirmationToken, PasswordResetToken
from utils.reset_password_email import reset_password_email
from django.conf import settings
from perfil.forms import (ResetPasswordForm, RequestResetPasswordForm,
                          ChangePasswordForm)


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
        usuario.is_active = False
        usuario.save()

        perfil = self.perfilform.save(commit=False)
        perfil.usuario = usuario
        perfil.save()

        # send_confirmation_email(usuario)
        send_confirmation_email(usuario)

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

        return redirect('perfil:criar')


@method_decorator(login_required, name='dispatch')
class Atualizar(BasePerfil):
    template_name = 'perfil/atualizar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        # Aqui ajustamos o userform para o contexto de atualização
        if self.request.user.is_authenticated:
            self.context['userform'] = perfil_forms.UserForm(
                data=self.request.POST or None,
                instance=self.request.user,
                usuario=self.request.user,
                updating=True,  # Agora estamos passando explicitamente que é uma atualização
            )

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):

        if not self.userform.is_valid() or not self.perfilform.is_valid():
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        # password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')

        # Usuários logados
        if self.request.user.is_authenticated:
            usuario = get_object_or_404(
                User, username=self.request.user.username)
            print(usuario.username)

            usuario.username = username

            # if password:
            #     usuario.set_password(password)

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

        # if password:
        #     autentica = authenticate(
        #         self.request,
        #         username=usuario,
        #         password=password
        #     )

        #     if autentica:
        #         login(self.request, user=usuario)

        messages.success(
            self.request,
            'Conta atualizada com sucesso!')

        return redirect('perfil:conta')


class ChangePasswordView(BasePerfil):

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        if self.request.user.is_authenticated:
            self.template_name = 'perfil/change_password.html' if self.request.user.is_authenticated else 'perfil/criar.html'

        self.context = {
            'active_setup': self.context['active_setup'],
            'form': perfil_forms.ChangePasswordForm(
                data=self.request.POST or None,
            )
        }

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = self.context['form']
        if not form.is_valid():
            return render(self.request, self.template_name, self.context)

        password = form.cleaned_data.get('password')
        user = self.request.user
        user.set_password(password)
        user.save()

        messages.success(
            self.request,
            'Senha alterada com sucesso!'
        )
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

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        total_recompensas = fidelidade_models.ComprasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_pontos_ganhos=models.Sum('pontos_adicionados'))
        print('total_recompensas: ', total_recompensas)
        total_ofertas = fidelidade_models.OfertasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_pontos_gastos=models.Sum('pontos_gastos'))
        print('total_ofertas: ', total_ofertas)
        total_recompensas_decimal = (
            total_recompensas['total_pontos_ganhos'] or 0)
        total_ofertas_decimal = total_ofertas['total_pontos_gastos'] or 0

        total_pontos = total_recompensas_decimal - total_ofertas_decimal
        print('total_pontos: ', total_pontos)

        self.context = {
            'active_setup': active_setup,
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
            'tipo_fidelidade': tipo_fidelidade,
        }

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)


class ConfirmarEmail(View):
    def get(self, request, token):
        # Tenta encontrar o token no banco de dados
        token = get_object_or_404(
            EmailConfirmationToken, token=token
        )
        print('token: ', token)
        print('token.user.is_active: ', token.user.is_active)
        # verifica se o token já foi utilizado ou expirou
        print('token.is_expired(): ', token.is_expired())
        if token.user.is_active or token.is_expired():
            messages.error(
                request,
                'Este link já foi utilizado ou expirou!'
            )
            return redirect('perfil:criar')

        # Ativa o usuário e salva no banco de dados
        token.user.is_active = True
        print('token.user.is_active: ', token.user.is_active)
        token.user.save()

        # Deleta o token do banco de dados
        # token.delete()

        messages.success(
            request,
            'Email confirmado com sucesso!'
        )
        return redirect('perfil:criar')


class RequestResetPasswordView(View):
    template_name = 'perfil/request_reset_password.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        self.context = {
            'active_setup': active_setup,
            'form': RequestResetPasswordForm() if not self.request.user.is_authenticated else None,
        }

    def get(self, request):
        # form = RequestResetPasswordForm()
        # renderizar o template com o formulário para digitar o email
        return render(self.request, self.template_name, self.context)

    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        form = RequestResetPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            reset_password_email(user)
            messages.success(
                request,
                'Email enviado com sucesso!'
            )
            return redirect('perfil:request_reset_password')
        else:
            messages.error(
                request,
                'Erro ao enviar o email!'
            )
            return redirect('perfil:request_reset_password')


class ResetPasswordView(View):
    # template_name = 'perfil/reset_password.html/{token}'

    def setup(self, *args, **kwargs):

        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        self.context = {
            'active_setup': active_setup,
        }

    def get(self, request, token):

        # Tenta encontrar o token no banco de dados
        print('token: ', token)
        token = get_object_or_404(
            PasswordResetToken, token=token
        )
        if request.user.is_authenticated:
            messages.error(
                request,
                'Você já está logado!'
            )
            return redirect('perfil:conta')

        # verifica se o token já foi utilizado ou expirou
        if token.is_expired() or token.used:
            messages.error(
                request,
                'Este link já foi utilizado ou expirou!'
            )
            return redirect('perfil:request_reset_password')

        form = ResetPasswordForm()

        # renderizar o template com o formulário para digitar a nova senha
        return render(
            request,
            'perfil/reset_password.html',
            {
                'active_setup': self.context['active_setup'],
                'form': form,
                'token': token
            }
        )

    def post(self, request, token):
        # Tenta encontrar o token no banco de dados
        reset_token = get_object_or_404(
            PasswordResetToken, token=token, used=False
        )

        # verifica se o token já foi utilizado ou expirou
        if reset_token.is_expired():
            messages.error(
                request,
                'Este link já foi utilizado ou expirou!'
            )
            return redirect('perfil:request_reset_password')

        # Atualiza a senha do usuário e salva no banco de dados
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = request.POST.get('password')
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            reset_token.used = True
            reset_token.save()
            # Redireciona para a página de login
            messages.success(
                request,
                'Senha alterada com sucesso!'
            )
            return redirect('perfil:criar')
        else:
            messages.error(
                request,
                'Erro ao alterar a senha!'
            )
            return render(
                request,
                'perfil/reset_password.html',
                {
                    'active_setup': self.context['active_setup'],
                    'form': form,
                    'token': token
                }
            )


class MovimentosCliente(BasePerfil):
    template_name = 'perfil/movimentos_cliente.html'

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

        compras_fidelidade = fidelidade_models.ComprasFidelidade.objects.filter(
            utilizador=self.request.user).order_by('-criado_em')

        # Calcular a diferença entre as compras e as ofertas
        ofertas_fidelidade = fidelidade_models.OfertasFidelidade.objects.filter(
            utilizador=self.request.user).order_by('-criado_em')
        total_compras = fidelidade_models.ComprasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_compras=models.Sum('pontos_adicionados'))
        total_ofertas = fidelidade_models.OfertasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_ofertas=models.Sum('pontos_gastos'))
        total_compras_decimal = (
            total_compras['total_compras'] or 0)
        print('total_compras_decimal: ', total_compras_decimal)
        total_ofertas_decimal = total_ofertas['total_ofertas'] or 0
        print('total_ofertas_decimal: ', total_ofertas_decimal)
        total_pontos = total_compras_decimal - total_ofertas_decimal

        # Combinar as consultas
        movimentos = []

        for compra in compras_fidelidade:
            movimentos.append(
                {
                    'data': compra.criado_em.strftime('%Y-%m-%d'),
                    'tipo': 'Compra',
                    'valor': compra.compra,
                    'pontos': compra.pontos_adicionados,
                    'cor': 'black',
                }
            )

        for oferta in ofertas_fidelidade:
            movimentos.append(
                {
                    'data': oferta.criado_em.strftime('%Y-%m-%d'),
                    'tipo': 'Oferta',
                    'valor': '-----',
                    'pontos': '-' + str(oferta.pontos_gastos),
                    'cor': 'red',
                }
            )

        # Ordenar os movimentos por data decrescente
        movimentos.sort(key=lambda x: x['data'], reverse=True)

        self.context = {
            'active_setup': active_setup,
            'compras_fidelidade': compras_fidelidade,
            'ofertas_fidelidade': ofertas_fidelidade,
            'tipo_fidelidade': tipo_fidelidade,
            'total_pontos': total_pontos,
            'movimentos': movimentos,
        }

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)
