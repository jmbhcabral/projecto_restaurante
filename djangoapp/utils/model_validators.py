from django.core.exceptions import ValidationError


def validate_png(image):
    if not image.name.lower().endswith('.png'):
        raise ValidationError('Imagem precisa ser .png')


def positive_price(value):
    if value < 0:
        raise ValidationError('O valor tem de ser positivo.')
