from django.db import models


class GoogleReview(models.Model):

    author_name = models.CharField(max_length=255)
    rating = models.IntegerField()
    text = models.TextField()
    time_created = models.DateTimeField()
    review_id = models.CharField(max_length=255, unique=True)
    profile_photo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.author_name} - {self.rating} estrelas"
