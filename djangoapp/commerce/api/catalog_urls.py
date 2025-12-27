# djangoapp/commerce/api/catalog_urls.py
from __future__ import annotations

from rest_framework.routers import DefaultRouter

from djangoapp.commerce.api.views.catalog import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="catalog-categories")
router.register(r"products", ProductViewSet, basename="catalog-products")

urlpatterns = router.urls