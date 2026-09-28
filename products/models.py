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

