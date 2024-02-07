from rest_framework.views import APIView
from rest_framework.response import Response
from restau.models import VersaoApp
from restau.serializers import VersaoAppSerializer


class UltimaVersaoAPIView(APIView):
    """
    API de versão da aplicação
    """

    def get(self, request):
        """
        Retorna a versão da aplicação
        """
        ultima_versao = VersaoApp.objects.latest('data_lancamento')
        serializer = VersaoAppSerializer(ultima_versao)
        return Response(serializer.data)
