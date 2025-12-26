# djangoapp/commerce/api/admin_urls.py
from __future__ import annotations

from commerce.api.views.admin_catalog import (
    AdminAddOnGroupViewSet,
    AdminAddOnOptionViewSet,
    AdminCategoryViewSet,
    AdminIngredientPriceViewSet,
    AdminIngredientViewSet,
    AdminProductDefaultIngredientViewSet,
    AdminProductPriceViewSet,
    AdminProductViewSet,
)
from commerce.api.views.admin_combos import (
    AdminComboChoiceGroupViewSet,
    AdminComboChoiceOptionViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Admin Catalog
router.register(r"categories", AdminCategoryViewSet, basename="admin-categories")
router.register(r"products", AdminProductViewSet, basename="admin-products")
router.register(r"ingredients", AdminIngredientViewSet, basename="admin-ingredients")
router.register(r"product-prices", AdminProductPriceViewSet, basename="admin-product-prices")
router.register(r"ingredient-prices", AdminIngredientPriceViewSet, basename="admin-ingredient-prices")
router.register(r"default-ingredients", AdminProductDefaultIngredientViewSet, basename="admin-default-ingredients")

router.register(r"addon-groups", AdminAddOnGroupViewSet, basename="admin-addon-groups")
router.register(r"addon-options", AdminAddOnOptionViewSet, basename="admin-addon-options")

router.register(r"combo-groups", AdminComboChoiceGroupViewSet, basename="admin-combo-groups")
router.register(r"combo-options", AdminComboChoiceOptionViewSet, basename="admin-combo-options")
urlpatterns = router.urls