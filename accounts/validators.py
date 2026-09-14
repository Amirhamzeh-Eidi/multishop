import re
from django.core.exceptions import ValidationError


PHONE_PATTERN = re.compile(r"^09\d{9}$")


def normalize_phone(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("Phone number must be a string.")

    value = value.strip()

    if not value:
        raise ValidationError("Phone number is required.")

    value = value.translate(
        str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789",
        )
    )

    value = re.sub(r"[\s\-\(\)\.]", "", value)

    if value.startswith("+98"):
        value = "0" + value[3:]

    elif value.startswith("0098"):
        value = "0" + value[4:]

    elif value.startswith("98"):
        value = "0" + value[2:]

    elif re.fullmatch(r"9\d{9}", value):
        value = "0" + value

    if not PHONE_PATTERN.fullmatch(value):
        raise ValidationError("Enter a valid mobile phone number.")

    return value