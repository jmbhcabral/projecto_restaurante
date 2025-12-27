from rest_framework import serializers

from djangoapp.fidelidade.models import ProdutoFidelidadeIndividual


class ProdutoFidelidadeIndividualSerializer(serializers.ModelSerializer):
    detalhes_fidelidade = serializers.CharField(
        source='fidelidade.nome', read_only=True)
    nome_produto = serializers.CharField(
        source='produto.nome', read_only=True)
    nome_categoria = serializers.CharField(
        source='produto.categoria.nome', read_only=True)
    nome_subcategoria = serializers.CharField(
        source='produto.subcategoria.nome', read_only=True)

    ordem_produto = serializers.IntegerField(
        source='produto.ordem', read_only=True)
    ordem_categoria = serializers.IntegerField(
        source='produto.categoria.ordem', read_only=True)
    ordem_subcategoria = serializers.IntegerField(
        source='produto.subcategoria.ordem', read_only=True)

    class Meta:
        model = ProdutoFidelidadeIndividual
        fields = (
            'id', 'fidelidade', 'detalhes_fidelidade', 'produto',
            'nome_produto', 'ordem_produto', 'nome_categoria',
            'ordem_categoria', 'nome_subcategoria', 'ordem_subcategoria',
            'pontos_recompensa', 'pontos_para_oferta', 'visibilidade'
        )


class DetalhesCompraSerializer(serializers.ModelSerializer):
    pontos_adicionados = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    criado_em = serializers.DateTimeField(read_only=True)


class DetalhesOfertaSerializer(serializers.ModelSerializer):
    pontos_gastos = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    criado_em = serializers.DateTimeField(read_only=True)


class TotalPontosSerializer(serializers.ModelSerializer):
    utilizador = serializers.CharField(
        max_length=100, read_only=True)
    tipo_fidelidade = serializers.CharField(
        max_length=100, allow_null=True, read_only=True)
    total_compras = serializers.IntegerField(read_only=True)
    total_ofertas = serializers.IntegerField(read_only=True)
    saldo_pontos = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    detalhes_compras = DetalhesCompraSerializer(many=True, read_only=True)
    detalhes_ofertas = DetalhesOfertaSerializer(many=True, read_only=True)
