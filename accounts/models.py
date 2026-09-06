from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from secrets import token_urlsafe
from  django.utils import timezone
from datetime import timedelta
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
def get_otp_expiration():
    return timezone.now() + timedelta(minutes=2)
class Otp(models.Model):
    identifier = models.CharField(max_length=20)
    token = models.CharField(max_length=100, default=token_urlsafe, unique=True, editable=False)
    code = models.CharField(max_length=4)
    expires_at = models.DateTimeField(default=get_otp_expiration)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
class Province(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
