# djangoapp/commerce/api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from djangoapp.commerce.api.views.cart import CartViewSet
from djangoapp.commerce.api.views.checkout import CheckoutViewSet
from djangoapp.commerce.api.views.combos import ComboViewSet

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"checkout", CheckoutViewSet, basename="checkout")
router.register(r"combos", ComboViewSet, basename="combos")

urlpatterns = [
    path("", include(router.urls)),
]