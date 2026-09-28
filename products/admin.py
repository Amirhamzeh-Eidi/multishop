from django.contrib import admin
from . import models
from django.utils.html import format_html


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1

    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Preview"


class ProductInformationValueInline(admin.TabularInline):
    model = models.ProductInformationValue
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 0
    show_change_link = True

    fields = ["variant_name", "stock", "price"]
    readonly_fields = ["variant_name"]

    template = "admin/products/product/product_variant_inline.html"

    def has_add_permission(self, request, obj=None):
        return False

    def variant_name(self, obj):
        attributes = ", ".join(
            str(item.value)
            for item in obj.variant_attributes.all()
        )
        return attributes or "-"

    variant_name.short_description = "Variant"


