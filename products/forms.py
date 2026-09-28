from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
class ProductVariantAttributeFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        attributes = set()
        for form in self.forms:
            if not form.cleaned_data:
                continue
            if form.cleaned_data.get("delete"):
                continue
            value = form.cleaned_data.get("value")
            if not value:
                continue
            attribute = value.attribute
            if attribute.pk in attributes:
                raise ValidationError("A variant cannot have more than one value for the same attribute.")
            attributes.add(attribute.pk)
