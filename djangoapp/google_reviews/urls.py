from django.urls import path

from .views import GoogleReviewsListView, UpdateGoogleReviewsView

app_name = 'google_reviews'

urlpatterns = [
    path('api/reviews/', GoogleReviewsListView.as_view(), name='google-reviews-list'),
    path('update-reviews/', UpdateGoogleReviewsView.as_view(), name='update-google-reviews'),
]