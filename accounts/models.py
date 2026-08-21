from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
class User(PermissionsMixin, AbstractBaseUser):
    phone = models.CharField(
        verbose_name="phone number",
        max_length=13,
        unique=True,
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        null=True, 
        blank=True
    )
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    profile = models.ImageField(upload_to="accounts/images", null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()

    USERNAME_FIELD = "phone"

    def __str__(self):
        return self.phone