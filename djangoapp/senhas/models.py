''' Módulo de models do app senhas '''

from django.db import models


class Senhas(models.Model):
    '''
    Modelo de senhas
    '''
    numero = models.IntegerField(
        verbose_name='Número',
        help_text='Número da senha',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.numero)


class FrasePub(models.Model):
    '''
    Modelo de frases públicas
    '''
    frase = models.CharField(
        max_length=150,
        verbose_name='Frase',
        help_text='Frase pública',
    )
    escolhida = models.BooleanField(
        verbose_name='Escolhida',
        help_text='Frase escolhida',
        default=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.frase)
