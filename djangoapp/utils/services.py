from datetime import datetime

import requests
from django.utils.timezone import make_aware
from google_reviews.models import GoogleReview


def fetch_and_store_google_reviews(api_key, place_id):
    
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'key': api_key,
        'fields': 'reviews',
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return False
    
    data = response.json()
    reviews = data.get('result', {}).get('reviews', [])

    for review in reviews:
        timestamp =review['time']
        dt = make_aware(datetime.fromtimestamp(timestamp))

        GoogleReview.objects.update_or_create(
            review_id=review['author_url'],
            defaults={
                'author_name': review['author_name'],
                'rating': review['rating'],
                'text': review['text'],
                'time_created': dt,
                'profile_photo_url': review.get('profile_photo_url', ''),
            }
        )
    return True