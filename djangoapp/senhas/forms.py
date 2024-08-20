''' Modulo de formulários para o app senhas '''

from django import forms
from .models import Senhas


class SenhasForm(forms.ModelForm):
    '''
    Formulário para adicionar uma número
    '''
    class Meta:
        '''
        Definição do modelo e campos do formulário
        '''
        model = Senhas
        fields = ['numero']

        numero = forms.IntegerField(
            label='Número',
            help_text='Número da senha',
        )

    def clean(self):
        '''

        Validação do campo numero
        O campo numero é obrigatório e deve ser entre 0 e 999

        '''
        cleaned_data = super().clean()
        numero = cleaned_data.get('numero')

        if numero is None:
            self.add_error('Numero', 'Número é obrigatório')
        elif numero < 0 or numero > 999:
            self.add_error('Numero', 'Número deve ser entre 0 e 999')
        return cleaned_data
