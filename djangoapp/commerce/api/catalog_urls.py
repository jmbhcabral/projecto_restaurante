# djangoapp/commerce/api/catalog_urls.py
from __future__ import annotations

from commerce.api.views.catalog import CategoryViewSet, ProductViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="catalog-categories")
router.register(r"products", ProductViewSet, basename="catalog-products")

urlpatterns = router.urls