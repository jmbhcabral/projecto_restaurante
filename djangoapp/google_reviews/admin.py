from django.contrib import admin

from djangoapp.google_reviews.models import GoogleReview


@admin.register(GoogleReview)
class GoogleReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'rating', 'time_created')
    search_fields = ('author_name', 'text')
    list_filter = ('rating', 'time_created')

