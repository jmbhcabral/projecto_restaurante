'''Este módulo contém as views para o aplicativo perfil.'''


from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views import View
from django.views.decorators.cache import never_cache
from fidelidade import models as fidelidade_models
from restau.models import ActiveSetup
from utils.email_confirmation import send_confirmation_email, send_reset_password_email
from utils.generate_reset_password_code import generate_reset_password_code
from utils.listar_compras_ofertas import listar_compras_ofertas
from utils.model_validators import (
    calcular_pontos_expirados,
    calcular_total_pontos,
    calcular_total_pontos_disponiveis,
)

from perfil import forms as perfil_forms
from perfil import models as perfil_models
from perfil.forms import RequestResetPasswordForm, ResetPasswordForm


class BasePerfil(View):
    '''Base class for the perfil views.'''

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

        self.renderizar = render(
            self.request,
            self.template_name,
            self.context
        )

    def get(self, *args, **kwargs):
        '''Get the base perfil.'''
        return self.renderizar


class Criar(BasePerfil):
    '''Create a new user.'''

    def post(self, *args, **kwargs):
        '''Create a new user.'''

        # Clean session data
        self.request.session.clear()

        if self.userform.is_valid() and self.perfilform.is_valid():
            username = self.userform.cleaned_data.get('username')
            email = self.userform.cleaned_data.get('email')
            password = self.userform.cleaned_data.get('password')
            first_name = self.userform.cleaned_data.get('first_name')
            last_name = self.userform.cleaned_data.get('last_name')
            code = generate_reset_password_code()
            perfil_data = self.convert_dates_to_str(self.perfilform.cleaned_data)
            
            # Garantir que apenas o ID do estudante seja armazenado
            if 'estudante' in perfil_data and perfil_data['estudante']:
                perfil_data['estudante'] = perfil_data['estudante'].id

            self.request.session['temp_user'] = {
                'username': username,
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'perfil_data': perfil_data,
                'code': code,
            }

            # Enviar email de confirmação
            send_confirmation_email(self.request, email, username, code)

            messages.success(
                self.request,
                'Verifique o seu email para criar a conta!')

            return redirect('perfil:user_verification_code')

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

    def convert_dates_to_str(self, data):
        """Convert date objects to strings in the data dictionary."""
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
        return data


class VerificationCodeView(BasePerfil):
    '''View for inserting the verification code.'''

    template_name = 'perfil/user_verification_code.html'

    def get(self, *args, **kwargs):
        '''GET method.'''
        if self.request.user.is_authenticated:
            return redirect('perfil:conta')

        return render(
            self.request,
            self.template_name,
            self.context
        )

    def post(self, *args, **kwargs):
        '''POST method.'''
        try:
            # Get the code from the post request
            code_1 = self.request.POST.get('code_1')
            code_2 = self.request.POST.get('code_2')
            code_3 = self.request.POST.get('code_3')

            # Verificar se os códigos são válidos antes de concatenar
            if not all([code_1, code_2, code_3]):
                messages.error(self.request, 'Código incompleto! Preencha todos os campos.')
                return render(self.request, self.template_name, self.context)

            # Criar o código final
            try:
                final_code = int(f'{code_1}{code_2}{code_3}')
            except ValueError:
                messages.error(self.request, 'Código inválido! Insira apenas números.')
                return render(self.request, self.template_name, self.context)

            # Get the user from the session
            temp_user = self.request.session.get('temp_user')

            # Check if the user exists in session
            if not temp_user or 'code' not in temp_user:
                messages.error(self.request, 'Utilizador não encontrado! Registe-se novamente.')
                return redirect('perfil:criar')

            # Check if the code is valid
            if str(temp_user['code']) != str(final_code):
                messages.error(self.request, 'Código inválido! Por favor, insira o código correto.')
                return render(self.request, self.template_name, self.context)

            # Criar o usuário
            user = User.objects.create_user(
                username=temp_user['username'],
                email=temp_user['email'],
                password=temp_user['password'],
                first_name=temp_user['first_name'],
                last_name=temp_user['last_name'],
            )

            # Criar o perfil do usuário
            perfil_data = temp_user.get('perfil_data', {})
            
            # Recuperar o objeto RespostaFidelidade apenas quando for criar o perfil
            estudante_id = perfil_data.pop('estudante', None)  # Remove e guarda o ID
            if estudante_id:
                try:
                    estudante = fidelidade_models.RespostaFidelidade.objects.get(id=estudante_id)
                    perfil = perfil_models.Perfil.objects.create(
                        usuario=user,
                        estudante=estudante,  # Passa o objeto diretamente
                        **perfil_data
                    )
                except fidelidade_models.RespostaFidelidade.DoesNotExist:
                    messages.error(self.request, 'Erro ao recuperar dados de fidelidade.')
                    return render(self.request, self.template_name, self.context)
            else:
                perfil = perfil_models.Perfil.objects.create(
                    usuario=user,
                    **perfil_data
                )

            messages.success(self.request, 'Código verificado com sucesso! Já pode aceder à sua conta.')
            
            # Apagar o temp_user da sessão
            self.request.session.pop('temp_user', None)
            
            return redirect('perfil:criar')

        except Exception as e:
            messages.error(self.request, f"Ocorreu um erro inesperado: {str(e)}")
            return redirect('perfil:criar')


@method_decorator(login_required, name='dispatch')
class Atualizar(BasePerfil):
    '''View for updating the user.'''
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
        '''GET method.'''
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        '''POST method.'''

        self.setup(*args, **kwargs)

        # Inicializa o userform novamente no método post
        self.context['userform'] = perfil_forms.UserForm(
            data=self.request.POST,
            instance=self.request.user,
            usuario=self.request.user,
            updating=True,  # Passa que é uma atualização
        )

        if self.context['userform'].is_valid() and self.context['perfilform'].is_valid():

            username = self.context['userform'].cleaned_data.get('username')
            email = self.context['userform'].cleaned_data.get('email')
            first_name = self.context['userform'].cleaned_data.get(
                'first_name')
            last_name = self.context['userform'].cleaned_data.get('last_name')

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

            messages.success(
                self.request,
                'Conta atualizada com sucesso!'
            )

            return redirect('perfil:conta')

        messages.error(
            self.request,
            'Não foi possivel atualizar o perfil! Verifique os erros nos campos!'
        )

        self.setup(*args, **kwargs)
        return self.renderizar


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
        hoje = timezone.now().date()
        pontos_hoje = fidelidade_models.ComprasFidelidade.objects.filter(
            utilizador=self.request.user,
            criado_em__date=hoje).aggregate(
                pontos_hoje=models.Sum('pontos_adicionados'))['pontos_hoje'] or 0
        pontos_hoje_decimal = Decimal(pontos_hoje)

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

        if ultima_presenca and ultima_presenca['ultima_actividade']:
            ultima_presenca = ultima_presenca['ultima_actividade'].date()
            tempo_para_expiracao_pontos = ultima_presenca + timedelta(days=45)
            dias_expiracao = (tempo_para_expiracao_pontos -
                              timezone.now().date()).days
        else:
            ultima_presenca = None
            tempo_para_expiracao_pontos = None
            dias_expiracao = None

        self.context = {
            'acesso_restrito': acesso_restrito,
            'active_setup': active_setup,
            'pontos_hoje_decimal': pontos_hoje_decimal,
            'total_pontos': total_pontos,
            'total_pontos_disponiveis': total_pontos_disponiveis,
            'total_pontos_ganhos_decimal': total_pontos_ganhos_decimal,
            'total_ofertas_decimal': total_ofertas_decimal,
            'total_pontos_expirados': total_pontos_expirados,
            'ultima_presenca': ultima_presenca,
            'data_expiracao': tempo_para_expiracao_pontos,
            'dias_expiracao': dias_expiracao,
        }

        print('Contexto: ', self.context)

        return render(self.request, self.template_name, self.context)

class CancelarConta(View):
    def post(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        user = self.request.user
        user_id = user.pk

        # Atualiza o usuário usando first()
        updated_user = User.objects.filter(id=user_id).first()
        if updated_user:
            updated_user.username = f'{user_id}-Cancelado'
            updated_user.email = f'{user_id}-cancelado@extremeway.pt'
            updated_user.first_name = f'{user_id}-Cancelado'
            updated_user.last_name = f'{user_id}-Cancelado'
            updated_user.is_active = False
            updated_user.save()

            # Atualiza a senha
            updated_user.set_password(f'{user_id:09d}')
            updated_user.save()

        # Atualiza o perfil
        perfil = perfil_models.Perfil.objects.filter(usuario=user).first()
        if perfil:
            perfil.telemovel = f'{user_id:09d}'
            perfil.data_cancelamento = timezone.now()
            perfil.save()

        messages.success(
            self.request,
            'Conta cancelada com sucesso!'
        )

        return JsonResponse({'message': 'Conta cancelada com sucesso!',
                             'redirect_url': reverse('perfil:criar')}, status=200)


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
    '''View for the request reset password.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = 'perfil/request_reset_password.html'
        self.context = {}

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
        '''GET method.'''
        if request.user.is_authenticated:
            return redirect('perfil:conta')
        # renderizar o template com o formulário para digitar o email
        return render(self.request, self.template_name, self.context)

    def post(self, request):
        '''POST method.'''

        # Clear the session
        self.request.session.clear()
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(
                request,
                'Email não encontrado!'
            )
            return redirect('perfil:request_reset_password')

        # Store the email in the session
        request.session['reset_password_email'] = email

        reset_code = generate_reset_password_code()

        user.perfil.reset_password_code = reset_code
        user.perfil.reset_password_code_expires = timezone.now()
        user.perfil.save()

        send_reset_password_email(request, email, reset_code)

        messages.success(
            request,
            'Email enviado com sucesso! Por favor, verifique seu email.'
        )
        return redirect('perfil:user_reset_code')


class ResetCodeView(View):
    '''View for the reset code.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = 'perfil/user_reset_verification_code.html'
        self.context = {}

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects\
            .order_by('-id')\
            .first()

        self.context = {
            'active_setup': active_setup,
            'allow_resend': False,
        }

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('perfil:conta')
        return render(request, self.template_name, self.context)

    def post(self, request):
        code_1 = request.POST.get('code_1')
        code_2 = request.POST.get('code_2')
        code_3 = request.POST.get('code_3')
        final_code = int(f'{code_1}{code_2}{code_3}')

        # Find the user with the reset code
        user = perfil_models.Perfil.objects.filter(
            reset_password_code=final_code).first()

        # Check if the code is valid
        if not final_code:
            messages.error(request, 'Código inválido!')
            return render(request, self.template_name, self.context)

        if user and user.reset_password_code_expires:
            # Check if the code has expired
            expiration_time = user.reset_password_code_expires + \
                timezone.timedelta(minutes=15)
            if timezone.now() > expiration_time:
                messages.error(
                    request,
                    'Código expirado! Por favor, solicite um novo.'
                )
                self.context['allow_resend'] = True
                return render(request, self.template_name, self.context)

            # Store the code in the session
            request.session['reset_code'] = final_code
            return redirect(
                'perfil:reset_password'
            )
        else:
            messages.error(request, 'Código inválido!')
            return render(request, self.template_name, self.context)


class ResendResetCodeView(View):
    '''View for resending the reset code.'''

    def post(self, request):
        '''POST method.'''

        # Get the email from the session
        email = request.session.get('reset_password_email', None)

        if not email:
            messages.error(
                request,
                'Não foi possível encontrar o email. '
                'Por favor, insira novamente.'
            )
            return redirect(
                'perfil:request_reset_password'
            )

        # Check if the email exists
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, 'Utilizador não encontrado!')
            return redirect(
                'perfil:request_reset_password'
            )

        reset_code = generate_reset_password_code()
        user.perfil.reset_password_code = reset_code
        user.perfil.reset_password_code_expires = timezone.now()
        user.perfil.save()

        send_reset_password_email(request, email, reset_code)

        messages.success(
            request,
            'Um novo código foi enviado.'
        )
        return redirect('perfil:user_reset_code')


class ResetPasswordView(View):
    '''View for the reset password.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = 'perfil/reset_password.html'
        self.context = {}

    def setup(self, *args, **kwargs):

        super().setup(*args, **kwargs)

        active_setup = ActiveSetup.objects \
            .order_by('-id') \
            .first()

        self.context = {
            'active_setup': active_setup,
        }

    def get(self, request):
        '''GET method.'''

        # Get the user from the session
        email = request.session.get('reset_password_email', None)

        user = User.objects.filter(email=email).first()

        if not email:
            messages.error(
                request,
                'Não foi possível encontrar o usuário. Por favor, tente novamente.'
            )
            return redirect('perfil:request_reset_password')

        if request.user.is_authenticated:
            messages.error(
                request,
                'Você já está logado!'
            )
            return redirect('perfil:conta')

        form = ResetPasswordForm()

        # renderizar o template com o formulário para digitar a nova senha
        return render(
            request,
            self.template_name,
            {
                'active_setup': self.context['active_setup'],
                'form': form,
                'user': user
            }
        )

    def post(self, request):
        '''POST method.'''

        # Get the user from the session
        email = request.session.get('reset_password_email', None)

        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(
                request,
                'Não foi possível encontrar o usuário. Por favor, tente novamente.'
            )
            return redirect('perfil:request_reset_password')

        # Atualiza a senha do usuário e salva no banco de dados
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = request.POST.get('password')
            user.set_password(new_password)
            user.save()

            # Limpar o código de redefinição para evitar reutilização
            user.perfil.reset_password_code = None
            user.perfil.reset_password_code_expires = None
            user.perfil.save()

            # Clear the session
            del request.session['reset_password_email']

            # Redireciona para a página de login
            messages.success(
                request,
                'Senha alterada com sucesso!'
            )
            return redirect('perfil:criar')

        messages.error(
            request,
            'Erro ao alterar a senha!'
        )
        return render(
            request,
            self.template_name,
            {
                'active_setup': self.context['active_setup'],
                'form': form,
                'user': user,
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

        # Listar compras e ofertas
        movimentos = listar_compras_ofertas(user)

        self.context = {
            'active_setup': active_setup,
            # 'compras_fidelidade': compras_fidelidade,
            # 'ofertas_fidelidade': ofertas_fidelidade,
            'tipo_fidelidade': tipo_fidelidade,
            'total_pontos': total_pontos,
            'total_pontos_disponiveis': total_pontos_disponiveis,
            'movimentos': movimentos,
        }

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return render(self.request, self.template_name, self.context)
