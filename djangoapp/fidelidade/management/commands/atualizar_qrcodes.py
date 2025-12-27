import json
from io import BytesIO

import qrcode
from django.core.files import File
from django.core.management.base import BaseCommand

from djangoapp.perfil.models import Perfil


class Command(BaseCommand):
    help = 'Atualiza os QR codes de todos os perfis'

    def handle(self, *args, **kwargs):
        perfis = Perfil.objects.select_related("usuario").all()

        for perfil in perfis:
            dados_perfil = {
                "Username": perfil.usuario.username,
                "Email": perfil.usuario.email,
                "NumeroCliente": perfil.numero_cliente,
                "DataNascimento": perfil.data_nascimento.isoformat() if perfil.data_nascimento else "",
                "Telemovel": perfil.telemovel,
            }

            dados_json = json.dumps(dados_perfil)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            qr.add_data(dados_json)
            qr.make(fit=True)

            img_qr = qr.make_image(fill_color="black", back_color="white")

            img_io = BytesIO()
            img_qr.save(img_io, format="PNG")
            img_io.seek(0)

            filename = f"qrcode_{perfil.numero_cliente}.png"
            perfil.qr_code.save(filename, File(img_io), save=True)

            self.stdout.write(self.style.SUCCESS(
                f"QR Code atualizado para {perfil.numero_cliente}"
            ))

        self.stdout.write(self.style.SUCCESS("Todos os QR Codes atualizados"))
