# djangoapp/commerce/models/product_image.py
from django.db import models
from django.db.models import Q


class ProductImage(models.Model):
    product = models.ForeignKey(
        "commerce.Product",
        on_delete=models.CASCADE,
        related_name="images",
    )

    # Source of truth: object path inside the GCS bucket
    gcs_path = models.CharField(max_length=500)

    # Optional convenience for frontend (public bucket). Can be derived.
    public_url = models.URLField(blank=True, null=True)

    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="uniq_primary_image_per_product",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.pk} - {self.gcs_path}"