""" Este módulo contém os serviços para o QR code do perfil do utilizador. """
# djangoapp/perfil/services/qr_service.py
from __future__ import annotations

from io import BytesIO

import qrcode
from django.core.files.base import File

from djangoapp.perfil.models import Perfil


def ensure_qr_code(perfil: Perfil) -> None:
    """
    Gera QR code uma única vez, quando:
    - existe numero_cliente
    - não existe qr_code
    """
    if not perfil.numero_cliente:
        return
    if perfil.qr_code:
        return

    numero_cliente_puro = "".join(filter(str.isdigit, perfil.numero_cliente))
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(numero_cliente_puro)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img_qr.save(img_io, "PNG")

    filename = f"qrcode_{perfil.numero_cliente}.png"
    perfil.qr_code.save(filename, File(img_io), save=False)
    perfil.save(update_fields=["qr_code"])