'''Este módulo contém as views para o aplicativo perfil.'''


from decimal import Decimal
import uuid
from utils.model_validators import (
    calcular_total_pontos, calcular_total_pontos_disponiveis,
    calcular_pontos_expirados
)
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta, date
from django.utils import timezone
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
from perfil.models import PasswordResetToken
from utils.reset_password_email import reset_password_email
from django.conf import settings
from perfil.forms import (ResetPasswordForm, RequestResetPasswordForm,
                          ChangePasswordForm)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


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

        self.renderizar = render(self.request, self.template_name,
                                 self.context)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):

        if self.userform.is_valid() and self.perfilform.is_valid():
            username = self.userform.cleaned_data.get('username')
            email = self.userform.cleaned_data.get('email')
            password = self.userform.cleaned_data.get('password')
            first_name = self.userform.cleaned_data.get('first_name')
            last_name = self.userform.cleaned_data.get('last_name')
            token = str(uuid.uuid4())
            perfil_data = self.convert_dates_to_str(
                self.perfilform.cleaned_data)

            # Armazenar os dados na sessão garantindo que
            # perfil_data armazene apenas IDs e valores simples
            if 'estudante' in perfil_data and perfil_data['estudante']:
                perfil_data['estudante'] = perfil_data['estudante'].id

            self.request.session['temp_user'] = {
                'username': username,
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'perfil_data': perfil_data,
                'token': token,
            }

            # Enviar email de confirmação
            self.send_confirmation_email(email, username, token)

            messages.success(
                self.request,
                'Conta criada com sucesso!\nVerifique o seu email para ativar a conta!')

            return redirect('perfil:criar')

        # Se o formulário não for válido, exibir os erros
        for form in [self.userform, self.perfilform]:
            # exibe os erros de cada campo sem exibir o campo para exibir os
            # campos substituir o values() por items()
            for errors in form.errors.values():
                for error in errors:
                    messages.error(
                        self.request,
                        error
                    )
        messages.error(
            self.request,
            'O formulário contém erros!'
        )
        # Redefine o contexto e re-renderiza a página com os erros
        self.setup(*args, **kwargs)
        return self.renderizar

    def send_confirmation_email(self, email, username, token):
        confirm_url = reverse('perfil:confirmar_email', args=[token])
        full_url = f"{self.request.scheme}://{self.request.get_host()}{confirm_url}"

        send_mail(
            'Confirmação de email',
            f'Olá {username},\n\n'
            'Para confirmar o seu email, por favor clique no link abaixo:\n\n'
            f'{full_url}\n\n'
            'Obrigado!',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

    def convert_dates_to_str(self, data):
        """Convert date objects to strings in the data dictionary."""
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
        return data


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

            usuario.username = username
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario
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

        messages.success(
            self.request,
            'Conta atualizada com sucesso!')

        return redirect('perfil:conta')


@method_decorator(login_required, name='dispatch')
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

    @method_decorator(never_cache)
    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.context)

    @method_decorator(never_cache)
    def post(self, *args, **kwargs):
        form = self.context['form']
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = self.request.user
            user.set_password(password)
            user.save()
            logout(self.request)
            self.request.session.flush()  # Limpa a sessão

            messages.success(
                self.request,
                'Senha alterada com sucesso!'
            )
            return redirect('perfil:criar')

        else:
            for error in form.errors.values():
                messages.error(
                    self.request,
                    error.as_text()
                )
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

        user = User.objects.filter(username=username).first()

        if user:
            if not user.is_active:
                resend_link = reverse('perfil:resend_confirmation_email', kwargs={
                                      'username': username})
                error_message = f'Verifique o seu email para ativar a conta!\nOu <a href="{resend_link}" style="text-decoration: underline;">clique aqui</a> para reenviar o email de confirmação!'
                messages.error(
                    self.request, mark_safe(error_message)

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


@method_decorator(login_required, name='dispatch')
class Conta(BasePerfil):
    template_name = 'perfil/conta.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        acesso_restrito = self.request.user.groups.filter(
            name='acesso_restrito').exists()

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        total_pontos_ganhos = fidelidade_models.ComprasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_pontos_ganhos=models.Sum('pontos_adicionados'))['total_pontos_ganhos'] or 0
        total_pontos_ganhos_decimal = Decimal(total_pontos_ganhos)

        total_ofertas = fidelidade_models.OfertasFidelidade.objects.filter(
            utilizador=self.request.user).aggregate(
            total_pontos_gastos=models.Sum('pontos_gastos'))['total_pontos_gastos'] or 0
        total_ofertas_decimal = Decimal(total_ofertas)

        total_pontos = calcular_total_pontos(self.request.user)
        total_pontos_disponiveis = calcular_total_pontos_disponiveis(
            self.request.user)
        total_pontos_expirados = calcular_pontos_expirados(self.request.user)

        ultima_presenca = perfil_models.Perfil.objects.filter(
            usuario=self.request.user).values('ultima_actividade').first()

        if ultima_presenca:
            ultima_presenca = ultima_presenca['ultima_actividade'].date()
            tempo_para_expiracao_pontos = ultima_presenca + timedelta(days=45)
            dias_expiracao = (tempo_para_expiracao_pontos -
                              timezone.now().date()).days
        else:
            tempo_para_expiracao_pontos = None
            dias_expiracao = None

        self.context = {
            'acesso_restrito': acesso_restrito,
            'active_setup': active_setup,
            'total_pontos': total_pontos,
            'total_pontos_disponiveis': total_pontos_disponiveis,
            'total_pontos_ganhos_decimal': total_pontos_ganhos_decimal,
            'total_ofertas_decimal': total_ofertas_decimal,
            'total_pontos_expirados': total_pontos_expirados,
            'ultima_presenca': ultima_presenca,
            'data_expiracao': tempo_para_expiracao_pontos,
            'dias_expiracao': dias_expiracao,
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


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class Regras(View):
    template_name = 'perfil/regras.html'

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
        # Tenta encontrar o token na sessao
        temp_user = request.session.get('temp_user', None)
        print('temp_user', temp_user)
        print('token from session', temp_user.get('token'))
        print('token from url', token)

        # verifica se o token já foi utilizado ou expirou
        if not temp_user or str(temp_user.get('token')) != str(token):
            messages.error(
                request,
                'Este link já foi utilizado ou está expirado!'
            )
            return redirect('perfil:criar')

        # Cria um novo usuário
        user = User.objects.create_user(
            username=temp_user['username'],
            email=temp_user['email'],
            password=temp_user['password'],
            first_name=temp_user['first_name'],
            last_name=temp_user['last_name'],
        )

        # Cria um perfil para o usuário
        perfil_data = temp_user['perfil_data']

        # Recuperar a instãncia de RespostaFidelidade usando o ID armazenado
        if 'estudante' in perfil_data and perfil_data['estudante']:
            perfil_data['estudante'] = fidelidade_models.RespostaFidelidade.objects.get(
                id=perfil_data['estudante'])

        perfil = perfil_models.Perfil.objects.create(
            usuario=user,
            **perfil_data
        )

        messages.success(
            request,
            'Email confirmado com sucesso!'
        )
        return redirect('perfil:criar')


class ResendConfirmationEmail(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        send_confirmation_email(user)
        messages.success(
            request,
            'Email de confirmação reenviado com sucesso. Por favor, verifique seu email.'
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
        # renderizar o template com o formulário para digitar o email
        return render(self.request, self.template_name, self.context)

    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        form = RequestResetPasswordForm(request.POST)

        if not user:
            messages.error(
                request,
                'Email não encontrado!'
            )
            return redirect('perfil:request_reset_password')

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
        token = get_object_or_404(
            PasswordResetToken, token=token
        )

        user = token.user

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
                'token': token,
                'user': user
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
                    'token': token,
                }
            )


@method_decorator(login_required, name='dispatch')
class MovimentosCliente(BasePerfil):
    '''View para mostrar os movimentos do cliente'''
    template_name = 'perfil/movimentos_cliente.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects.order_by('-id').first()
        user = self.request.user

        if not user.is_authenticated:
            return redirect('perfil:criar')

        perfil = user.perfil
        tipo_fidelidade = perfil.tipo_fidelidade

        # Calcular o total de pontos
        total_pontos = calcular_total_pontos(user)

        # Calcular pontos disponíveis
        total_pontos_disponiveis = calcular_total_pontos_disponiveis(user)

        compras_fidelidade = fidelidade_models.ComprasFidelidade.objects.filter(
            utilizador=user).order_by('-criado_em')

        ofertas_fidelidade = fidelidade_models.OfertasFidelidade.objects.filter(
            utilizador=user).order_by('-criado_em')

        movimentos = []

        agora = timezone.now()
        for compra in compras_fidelidade:
            criado_em_local = timezone.localtime(compra.criado_em)
            disponivel_amanha = agora.date() <= criado_em_local.date()
            expirado = compra.expirado

            movimentos.append({
                'data': criado_em_local.strftime('%Y-%m-%d'),
                'tipo': 'Compra',
                'valor': compra.compra,
                'pontos': compra.pontos_adicionados,
                'cor': 'orange' if disponivel_amanha else 'black',
                'disponivel_amanha': disponivel_amanha,
                'expirado': expirado,
            })

        for oferta in ofertas_fidelidade:
            processado = oferta.processado
            movimentos.append({
                'data': oferta.criado_em.strftime('%Y-%m-%d'),
                'tipo': 'Oferta',
                'valor': '-----',
                'pontos': '-' + str(oferta.pontos_gastos),
                'cor': 'red',
                'processado': processado,
            })

        # Ordenar os movimentos por data decrescente
        movimentos.sort(key=lambda x: x['data'], reverse=True)

        self.context = {
            'active_setup': active_setup,
            'compras_fidelidade': compras_fidelidade,
            'ofertas_fidelidade': ofertas_fidelidade,
            'tipo_fidelidade': tipo_fidelidade,
            'total_pontos': total_pontos,
            'total_pontos_disponiveis': total_pontos_disponiveis,
            'movimentos': movimentos,
        }

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)
