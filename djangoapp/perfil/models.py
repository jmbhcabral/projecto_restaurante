from django.db import models
from django.contrib.auth.models import User
from fidelidade.models import Fidelidade
from django.utils import timezone
from django.forms import ValidationError
from utils.model_validators import validar_nif
import qrcode
from io import BytesIO
from django.core.files import File
import uuid
import json


class Perfil(models.Model):
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        verbose_name="Utilizador",
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
    estudante = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Estudante",

        choices=(
            ('escola_sec_ramada', 'Sim, na Esc. Sec. Ramada'),
            ('agrup_vasco_santana', 'Sim no Agrup. Vasco Santana'),
            ('outra_escola', 'Sim, noutra escola'),
            ('nao', 'Não'),
        ),
        help_text='Se estudante, indique a escola onde estuda.',
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

    def save(self, *args, **kwargs):
        # Atualiza a data da última atualização da data de nascimento
        if self.pk:
            original = Perfil.objects.get(pk=self.pk)
            if original.data_nascimento != self.data_nascimento:
                agora = timezone.now()

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

        if self.estudante == 'escola_sec_ramada' or \
                self.estudante == 'agrup_vasco_santana':
            fidelidade_obj = Fidelidade.objects.get(nome='Estudante')
            self.tipo_fidelidade = fidelidade_obj

        else:
            fidelidade_obj = Fidelidade.objects.get(nome='Artesanal')
            self.tipo_fidelidade = fidelidade_obj

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


def generate_uuid():
    return str(uuid.uuid4())


class EmailConfirmationToken(models.Model):
    class Meta:
        verbose_name = "EmailConfirmation"
        verbose_name_plural = "EmailConfirmations"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="User",
    )
    token = models.CharField(max_length=100, default=generate_uuid)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        # Expira em 48 horas
        tempo_expiracao = self.created_at + timezone.timedelta(hours=48)
        print('created_at', self.created_at)
        print('timezone.now()', timezone.now())
        print('tempo_expiracao', tempo_expiracao)
        return tempo_expiracao < timezone.now()

    def __str__(self):
        return self.token


class PasswordResetToken(models.Model):
    class Meta:
        verbose_name = "PasswordResetToken"
        verbose_name_plural = "PasswordResetTokens"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="User",
    )
    token = models.CharField(max_length=100, default=generate_uuid)
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)

    def is_expired(self):
        # Expira em 24 horas
        tempo_expiracao = self.created_at + timezone.timedelta(hours=24)
        print('created_at', self.created_at)
        print('timezone.now()', timezone.now())
        print('tempo_expiracao', tempo_expiracao)
        return tempo_expiracao < timezone.now()

    def __str__(self):
        return self.token
