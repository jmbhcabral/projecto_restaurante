from django.contrib import admin

from djangoapp.commerce.models import (
    AddOnGroup,
    AddOnOption,
    Cart,
    CartItem,
    CartItemAddOn,
    CartItemRemovedIngredient,
    Category,
    Ingredient,
    IngredientPrice,
    Order,
    OrderItem,
    OrderItemAddOn,
    OrderItemRemovedIngredient,
    Product,
    ProductDefaultIngredient,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")


class ProductDefaultIngredientInline(admin.TabularInline):
    model = ProductDefaultIngredient
    extra = 1


class AddOnGroupInline(admin.TabularInline):
    model = AddOnGroup
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "base_price", "status", "is_sellable")
    search_fields = ("sku", "name")
    list_filter = ("status", "is_sellable", "category")
    inlines = [ProductDefaultIngredientInline, AddOnGroupInline]


class AddOnOptionInline(admin.TabularInline):
    model = AddOnOption
    extra = 1


@admin.register(AddOnGroup)
class AddOnGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "min_select", "max_select")
    search_fields = ("name", "product__sku", "product__name")
    inlines = [AddOnOptionInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(IngredientPrice)
class IngredientPriceAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "price", "valid_from", "created_at")
    list_filter = ("ingredient",)
    ordering = ("ingredient", "-valid_from")


# Carts / Orders (optional in admin; keep read-only in real ops)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(CartItemAddOn)
admin.site.register(CartItemRemovedIngredient)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderItemAddOn)
admin.site.register(OrderItemRemovedIngredient)