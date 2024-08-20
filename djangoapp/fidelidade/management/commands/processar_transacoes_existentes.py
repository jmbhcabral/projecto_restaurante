'''Este script processa todas as transações existentes para todos os perfis de utilizadores'''

from django.core.management.base import BaseCommand
from perfil.models import Perfil
from utils.model_validators import processar_transacoes_existentes


class Command(BaseCommand):
    '''
    Classe de comando para processar transações existentes
    '''
    help = 'Processa transações existentes para identificar e expirar pontos antigos'

    def handle(self, *args, **kwargs):
        processar_transacoes_existentes()
        self.stdout.write(self.style.SUCCESS(
            'Transações processadas com sucesso.'))
