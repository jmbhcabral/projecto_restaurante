from django.db import models
from django.contrib.auth.models import User
from fidelidade.models import Fidelidade
from django.utils import timezone
from django.forms import ValidationError
from utils.model_validators import validar_nif
import qrcode
from io import BytesIO
from django.core.files import File


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

    def save(self, *args, **kwargs):
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

        # super().save(*args, **kwargs)

        # Crie um QRCode com base nas informações do perfil
        dados_perfil = f"Username: {self.usuario}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(dados_perfil)
        qr.make(fit=True)

        # Crie uma imagem QRCode
        img_qr = qr.make_image(fill_color="black", back_color="white")

        # Salve a imagem QRCode no campo qr_code
        img_io = BytesIO()
        img_qr.save(img_io, 'PNG')
        self.qr_code.save(
            f'qrcode_{self.usuario}.png', File(img_io), save=False)

        if self.estudante == 'escola_sec_ramada' or \
                self.estudante == 'agrup_vasco_santana':
            fidelidade_obj = Fidelidade.objects.get(nome='Estudante')
            self.tipo_fidelidade = fidelidade_obj

        else:
            fidelidade_obj = Fidelidade.objects.get(nome='Artesanal')
            self.tipo_fidelidade = fidelidade_obj

        super().save(*args, **kwargs)

    def clean(self):

        error_messages = {}

        if not self.data_nascimento:
            error_messages['data_nascimento'] = 'Data de Nascimento \
            é obrigatória.'

        if not self.telemovel or len(self.telemovel) != 9:
            error_messages['telemovel'] = 'Telemóvel é obrigatório e tem de \
                ter 9 digitos.'

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
