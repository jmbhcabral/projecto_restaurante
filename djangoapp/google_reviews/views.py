import os

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.services import fetch_and_store_google_reviews


class GoogleReviewsListView(APIView):
    '''
    API para listar as reviews do Google Maps
    '''
    def get(self, request):
        print('teste2')
        place_id = 'ChIJTw4Gkr4tGQ0R83HBmnAxO9Y'
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')

        url = 'https://maps.googleapis.com/maps/api/place/details/json'
        params = {
            'place_id': place_id,
            'key': api_key,
            'fields': 'reviews',
        }
        response = requests.get(url, params=params)
        print(response.json())
        if response.status_code == 200:
            data = response.json()
            data_length = len(data.get('result', {}).get('reviews', []))
            print(data_length)
            reviews = data.get('result', {}).get('reviews', [])
            return Response(reviews, status=status.HTTP_200_OK)
        
        return Response({'error': 'Erro ao buscar reviews'}, status=status.HTTP_400_BAD_REQUEST)
        

class UpdateGoogleReviewsView(APIView):
    def post(self, request):
        place_id = 'ChIJTw4Gkr4tGQ0R83HBmnAxO9Y'
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')

        success = fetch_and_store_google_reviews(api_key, place_id)

        if success:
            return Response({'message': 'Reviews atualizadas com sucesso'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Erro ao atualizar reviews'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)