from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import (ProdutoFidelidadeIndividual, ComprasFidelidade,
                      OfertasFidelidade
                      )
from ..serializers import ProdutoFidelidadeIndividualSerializer
from collections import defaultdict
from django.db.models import Sum, Min
from utils.model_validators import (
    calcular_total_pontos, calcular_dias_para_expirar, 
    calcular_pontos_indisponiveis, calcular_total_pontos_disponiveis,
    calcular_pontos_expirados
    )
from decimal import Decimal


class ProdutoFidelidadeAPI(APIView):
    """
    API para listar os produtos de fidelidade
    """

    def get(self, request, *args, **kwargs):
        """
        Lista todos os produtos de fidelidade
        """
        user = request.user

        if not user.is_authenticated:
            return Response(
                {'detail': 'Não autorizado'},
                status=401,
            )

        if user.perfil.tipo_fidelidade:

            tipo_fidelidade = user.perfil.tipo_fidelidade
            produtos_fidelidade = ProdutoFidelidadeIndividual.objects.filter(
                fidelidade=tipo_fidelidade, visibilidade=True).order_by(
                    'produto__categoria__ordem', 'produto__subcategoria__ordem',
                    'produto__ordem'
            )
            serializer = ProdutoFidelidadeIndividualSerializer(
                produtos_fidelidade, many=True)
            data = serializer.data

            # Restruturar dados para serem apresentados no frontend
            categorias = defaultdict(lambda: defaultdict(list))
            for item in data:
                categoria = item['nome_categoria']
                subcategoria = item.get('nome_subcategoria')
                if categoria:  # Verificar se existe categoria
                    produto = {
                        'nome_produto': item['nome_produto'],
                        'pontos_recompensa': item['pontos_recompensa'],
                        'pontos_para_oferta': item['pontos_para_oferta'],
                    }
                    if subcategoria:
                        categorias[categoria][subcategoria].append(produto)
                    else:
                        categorias[categoria]['Sem subcategoria'].append(
                            produto)
            # Remover categorias e subcategorias vazias
            categorias = {cat: subcats for cat,
                          subcats in categorias.items() if subcats}
            for cat in categorias:
                categorias[cat] = {subcat: prods for subcat,
                                   prods in categorias[cat].items() if prods}

            # Converter a estrutura de dicionario para uma lista de categorias
            resultado_ordenado = []
            for categoria, subcats in categorias.items():
                categoria_dict = {
                    'categoria': categoria,
                    'subcategorias': []
                }
                for subcategoria, produtos in subcats.items():
                    if produtos:  # Verificar se existe produtos
                        subcategoria_dict = {
                            'subcategoria': subcategoria,
                            'produtos': produtos
                        }
                        categoria_dict['subcategorias'].append(
                            subcategoria_dict)
                # Verificar se existe subcategorias
                if categoria_dict['subcategorias']:
                    resultado_ordenado.append(categoria_dict)

            # Construir o objecto da resposta final
            resposta_final = {
                'tipo_fidelidade': tipo_fidelidade.nome,
                'categorias': resultado_ordenado
            }

            return Response(resposta_final)
        else:
            return Response(
                {'detail': 'Não tem um tipo de fidelidade atribuído'},
                status=400,
            )


class TotalPontosAPIV1(APIView):
    """

    API para listar o total de pontos de fidelidade
    """

    def get(self, request, *args, **kwargs):
        """
        Lista o total de pontos de fidelidade
        """
        user = request.user

        if not user.is_authenticated:
            return Response(
                {'detail': 'Não autorizado'},
                status=401,
            )

        if user.perfil.tipo_fidelidade:
            tipo_fidelidade = user.perfil.tipo_fidelidade if hasattr(
                user, 'perfil') else None

            compras_fidelidade = ComprasFidelidade.objects.filter(
                fidelidade=tipo_fidelidade, utilizador=user
            )


            ofertas_fidelidade = OfertasFidelidade.objects.filter(
                fidelidade=tipo_fidelidade, utilizador=user
            )

            total_compras = compras_fidelidade.count()
            total_ofertas = ofertas_fidelidade.count()
            total_visitas = total_compras + total_ofertas

            # Detalhes de compras e ofertas
            detalhes_compras = [
                {
                    "compra": compra.compra,
                    "pontos_adicionados": compra.pontos_adicionados,
                    "expirado": compra.expirado,
                    "criado_em": compra.criado_em,
                }
                for compra in compras_fidelidade
            ]

            detalhes_ofertas = [
                {
                    "pontos_gastos": oferta.pontos_gastos,
                    "criado_em": oferta.criado_em,
                }
                for oferta in ofertas_fidelidade
            ]

            total_pontos_adicionados = sum(
                [compra.pontos_adicionados for compra in compras_fidelidade if compra.pontos_adicionados]
            )

            print('total_pontos_adicionados', total_pontos_adicionados)
            total_pontos_gastos = sum(
                [oferta.pontos_gastos for oferta in ofertas_fidelidade if oferta.pontos_gastos]
            )

            print('total_pontos_gastos', total_pontos_gastos)

            saldo_pontos = calcular_total_pontos(user)

            pontos_disponiveis = calcular_total_pontos_disponiveis(user)

            pontos_indisponiveis = calcular_pontos_indisponiveis(user)

            dias_para_expirar = calcular_dias_para_expirar(user) if total_compras > 0 and saldo_pontos > 0 else 0

            total_pontos_expirados = calcular_pontos_expirados(user)

            resposta = {
                "utilizador": user.id,
                "tipo_fidelidade": tipo_fidelidade.nome if tipo_fidelidade else None,
                "total_pontos_ganhos": total_pontos_adicionados,

                "total_pontos_gastos": total_pontos_gastos,
                "total_compras": total_compras,
                "total_ofertas": total_ofertas,
                "total_visitas": total_visitas,
                "total_pontos_expirados": total_pontos_expirados,
                "pontos": saldo_pontos,
                "pontos_disponiveis": pontos_disponiveis,
                "pontos_indisponiveis": pontos_indisponiveis,
                "dias_para_expirar": dias_para_expirar,
                "detalhes_compras": detalhes_compras,
                "detalhes_ofertas": detalhes_ofertas,

            }

            return Response(resposta)