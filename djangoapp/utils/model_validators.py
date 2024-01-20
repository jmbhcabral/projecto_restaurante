from django.core.exceptions import ValidationError


def validate_png(image):
    if not image.name.lower().endswith('.png'):
        raise ValidationError('Imagem precisa ser .png')


def positive_price(value):
    if value < 0:
        raise ValidationError('O valor tem de ser positivo.')


def validar_nif(nif):
    # Remover espaços em branco e outros caracteres não numéricos
    nif = ''.join(filter(str.isdigit, nif))

    # Verificar se o NIF tem 9 dígitos após remover caracteres não numéricos
    if len(nif) != 9:
        return False

    # Converter o NIF para uma lista de inteiros
    nif_digitos = [int(digito) for digito in nif]

    # Verificar o dígito de controlo
    total = 0
    for i in range(8):
        total += nif_digitos[i] * (9 - i)

    resto = total % 11
    digito_controlo_calculado = 11 - resto if resto != 0 and resto != 1 else 0

    return digito_controlo_calculado == nif_digitos[8]


# Model ProdutoFidelidadeIndividual

def calcular_pontos(produto, fidelidade):
    ementa = fidelidade.ementa
    preco_field = ementa.nome_campo_preco_selecionado
    preco = getattr(produto, preco_field)
    if preco is None:
        raise ValueError(
            f'O produto {produto} não tem um preço definido no campo '
            f'{preco_field}'
        )
    preco_int = int(preco * 100)
    desconto = fidelidade.desconto
    pontos_necessarios = int(preco_int / (desconto / 100))
    return preco_int, pontos_necessarios
