from django.db import models
from django.template.defaultfilters import slugify 
from django.core.exceptions import ValidationError
# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(blank=True, unique=True)
    image = models.ImageField(upload_to="products/img/brands")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    short_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.SET_NULL, blank=True, null=True)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Attribute(models.Model):
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name
    
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="values")
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    stock = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        if not self.pk:
            return "Unsaved Product Variant"

        attributes = ", ".join(
            item.value
            for item in self.variant_attributes.select_related("value")
        )

        return f"{self.product.name} - {attributes or 'Default'}"

class ProductVariantAttribute(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="variant_attributes",
    )

    value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        related_name="variant_attributes",
    )
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="variants", blank=True, null=True, editable=False)
    def save(self, *args, **kwargs):
        self.attribute = self.value.attribute
        super().save(*args, **kwargs)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["variant", "value"], name="unique_variant_value"),
            models.UniqueConstraint(fields=[ "variant","attribute"], name="unique_variant_attribute")
        ]

