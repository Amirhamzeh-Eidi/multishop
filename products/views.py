from django.shortcuts import render

# Create your views here.
class ProductDetailView(DetailView):
    model = models.Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attributes = {}
        product = self.object
        variants = product.variants.all()
        for variant in variants:
            for variant_attribute in variant.variant_attributes.all():
                if attributes.get(variant_attribute.attribute.name):
                    if not variant_attribute.value.value in attributes[variant_attribute.attribute.name]:
                        attributes[variant_attribute.attribute.name].append(variant_attribute.value.value)
                else:
                    attributes[variant_attribute.attribute.name] = [variant_attribute.value.value]
        print(attributes)
        product_images = product.images.all()
        main_image = product.images.all().filter(is_main=True, product=product)
        main_image = main_image if main_image.exists() else product_images[:1]
        context["main_image"] = main_image
        context["attributes"] = attributes
        return context
    