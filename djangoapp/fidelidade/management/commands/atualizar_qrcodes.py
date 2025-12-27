import json
from io import BytesIO

import qrcode
from django.core.files import File
from django.core.management.base import BaseCommand

from djangoapp.perfil.models import Perfil


class Command(BaseCommand):
    help = 'Atualiza os QR codes de todos os perfis'

    def handle(self, *args, **kwargs):
        perfis = Perfil.objects.all()
        for perfil in perfis:
            # Gere o QR Code com base nas informações do perfil
            dados_perfil = {
                "Username": perfil.usuario.username,
                "Email": perfil.usuario.email,
                "NumeroCliente": perfil.numero_cliente,
                "DataNascimento": perfil.data_nascimento.isoformat() if perfil.data_nascimento else "",
                "Telemovel": perfil.telemovel,
            }

            # Convertendo os dados para JSON
            dados_json = json.dumps(dados_perfil)

            # Configuração do Qr Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            # Adicionando os dados JSON ao Qr Code
            qr.add_data(dados_json)
            qr.make(fit=True)

            # Criar um buffer para o QR Code
            img_qr = qr.make_image(fill_color="black", back_color="white")

            img_io = BytesIO()
            img_qr.save(img_io, 'PNG')
            filename = f'qrcode_{perfil.numero_cliente}.png'
            perfil.qr_code.save(
                filename, File(img_io), save=True)

            print(f'QR Code atualizado para {perfil.numero_cliente}')
            self.stdout.write(self.style.SUCCESS(
                f'QR Code atualizado para {perfil.numero_cliente}'
            ))

        print('Todos os QR Codes atualizados')
