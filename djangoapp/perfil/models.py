''' Este módulo contém os modelos de dados para o aplicativo de perfil. '''

import uuid
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now
from io import BytesIO
from django.core.files import File
from django.db import models
from django.forms import ValidationError
from django.contrib.auth import get_user_model
from fidelidade.models import Fidelidade, RespostaFidelidade, Respostas
from utils.model_validators import validar_nif
import qrcode

User = get_user_model()

class Perfil(models.Model):
    ''' Model for the user profile. '''
    class Meta:
        ''' Meta class for the Perfil model. '''
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        verbose_name="Utilizador",
        related_name='perfil',
    )
    data_nascimento = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    telemovel = models.CharField(
        max_length=9,
        blank=True,
        verbose_name="Telemóvel",
    )
    nif = models.CharField(max_length=9, blank=True)

    qr_code = models.ImageField(
        upload_to='assets/qrcodes/', blank=True, null=True)

    numero_cliente = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        verbose_name="Número Cliente",
    )
    estudante = models.ForeignKey(
        RespostaFidelidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Estudante",
    )
    tipo_fidelidade = models.ForeignKey(
        Fidelidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo Fidelidade",
    )

    ultima_atualizacao_data_nascimento = models.DateTimeField(
        null=True, blank=True)

    ultima_actividade = models.DateTimeField(
        default=timezone.now,
        verbose_name="Última Actividade",
        blank=True,
        null=True,
    )
    reset_password_code = models.IntegerField(
        verbose_name="Código de Reset de Password",
        blank=True,
        null=True,
        default=000000000
    )
    reset_password_code_expires = models.DateTimeField(
        verbose_name="Expiração do Código de Reset de Password",
        blank=True,
        null=True,
        default=timezone.now
    )
    data_cancelamento = models.DateTimeField(
        verbose_name="Data de Cancelamento",
        blank=True,
        null=True,
    )
    notificacoes_email = models.BooleanField(
        verbose_name="Notificações por Email",
        default=True,
    )
    notificacoes_telemovel = models.BooleanField(
        verbose_name="Notificações por Telemóvel",
        default=True,
    )
    first_login = models.BooleanField(
        verbose_name="Primeiro Login",
        default=True,
    )

    def save(self, *args, **kwargs):
        # Atualiza a data da última atualização da data de nascimento
        print('self.pk: ', self.pk)
        if self.pk:
            original = Perfil.objects.get(pk=self.pk)
        
            # Verifica se a data de nascimento foi alterada
            if original.data_nascimento != self.data_nascimento:
                agora = timezone.now()
                ultima_atualizacao = self.ultima_atualizacao_data_nascimento

                # Se há uma última atualização, verifica o período mínimo
                if ultima_atualizacao:
                    periodo_minimo = ultima_atualizacao + timezone.timedelta(days=182.5)  # 6 meses
                    if agora < periodo_minimo:
                        return
                
                # Atualiza a data da última alteração se a regra for cumprida
                self.ultima_atualizacao_data_nascimento = agora

        # Gera o número de cliente
        if not self.numero_cliente:
            ultimo_numero_cliente = Perfil.objects.all().order_by(
                'id').last()
            if ultimo_numero_cliente is not None and \
                    ultimo_numero_cliente.numero_cliente.startswith('CEW-'):
                ultimo_numero_cliente = int(
                    ultimo_numero_cliente.numero_cliente.split('-')[1])
                novo_numero = ultimo_numero_cliente + 1

            else:
                novo_numero = 1050  # número de cliente inicial

            self.numero_cliente = f'CEW-{novo_numero}'

        if self.estudante:
            # Aqui obtemos a instância de Fidelidade associada ao RespostaFidelidade
            self.tipo_fidelidade = self.estudante.tipo_fidelidade
        else:
            self.tipo_fidelidade = None

        # Crie um QRCode com base nas informações do perfil
        numero_cliente_puro = ''.join(filter(str.isdigit, self.numero_cliente))

        # Configuração do Qr Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        # Adicionando os dados JSON ao Qr Code
        qr.add_data(numero_cliente_puro)
        qr.make(fit=True)

        # Crie uma imagem QRCode
        img_qr = qr.make_image(fill_color="black", back_color="white")

        # Salve a imagem QRCode no campo qr_code
        img_io = BytesIO()
        img_qr.save(img_io, 'PNG')
        # Usando o número de cliente como nome do ficheiro
        filename = f'qrcode_{self.numero_cliente}.png'
        self.qr_code.save(
            filename, File(img_io), save=False)

        super().save(*args, **kwargs)

    def clean(self):

        error_messages = {}

        if not self.data_nascimento:
            error_messages['data_nascimento'] = 'Data de Nascimento \
            é obrigatória.'

        # Atualiza a data da última atualização da data de nascimento
        if self.pk:
            original = Perfil.objects.get(pk=self.pk)
            if original.data_nascimento != self.data_nascimento:
                agora = timezone.now()
                if self.ultima_atualizacao_data_nascimento:
                    # 6 meses = aproximadamente 182.5 dias
                    periodo_minimo = self.ultima_atualizacao_data_nascimento + \
                        timezone.timedelta(days=182.5)
                    if agora < periodo_minimo:
                        error_messages['data_nascimento'] = (
                            'A data de nascimento só pode ser alterada \
                            passados 6 meses da última alteração.')
                self.ultima_atualizacao_data_nascimento = agora

        if self.nif and not validar_nif(self.nif):
            error_messages['nif'] = 'NIF inválido.'

        raise ValidationError(error_messages)

    def __str__(self):
        return f'{self.usuario.first_name} {self.usuario.last_name}'


class Morada(models.Model):
    class Meta:
        verbose_name = "Morada"
        verbose_name_plural = "Moradas"

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
    )
    finalidade_morada = models.CharField(blank=False, choices=(
        ('E', 'Entrega'),
        ('F', 'Faturação')
    )
    )
    morada = models.CharField(max_length=100, blank=True)
    numero = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Número",)
    codigo_postal = models.CharField(
        max_length=4,
        blank=True,
        verbose_name="Código Postal",)
    ext_codigo_postal = models.CharField(
        max_length=3,
        blank=True,
        verbose_name="Extensão Código Postal",)

    def clean(self):
        error_messages = {}
        if not self.morada:
            error_messages['morada'] = 'Morada é obrigatória.'

        if not self.numero:
            error_messages['numero'] = 'Número é obrigatório.'

        if not self.codigo_postal:
            error_messages['codigo_postal'] = 'Código Postal é obrigatório.'

        if not self.ext_codigo_postal:
            error_messages['ext_codigo_postal'] = 'Extensão Código Postal é obrigatória.'

        raise ValidationError(error_messages)

    def __str__(self):
        return self.finalidade_morada


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return now() > self.created_at + timedelta(minutes=15)  # Expira em 15 minutos

    def __str__(self):
        return f"Reset Token for {self.user.email}"