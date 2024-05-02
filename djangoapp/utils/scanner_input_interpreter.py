import sys

dados_exemplo = "AÇ210057416(BÇ999999990(CÇPT(DÇFS(EÇN(FÇ20240430(GÇFS 1A2401-252(HÇJF3MZJ5D'252(I1ÇPT(I7Ç7.56(I8Ç1.74(NÇ1.74(OÇ9.30(QÇYeO»(RÇ196"


def interpretar_dados(dados):
    # Dicionário para guardar os dados interpretados
    dados_interpretados = {}

    # Extrai as partes dos dados baseando-se nos parênteses
    partes = dados.strip().split('(')
    for parte in partes:
        if parte:
            # O primeiro carácter até 'Ç' é o identificador, o restante é o valor
            indice = parte.find('Ç')
            if indice != -1:
                chave = parte[:indice]
                valor = parte[indice + 1:].strip("'")
                dados_interpretados[chave] = valor

    print('Dados recebidos:', dados_interpretados)

    return dados_interpretados
