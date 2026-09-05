from django.db import models 
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone, email=None, password=None, **extrfields):
        if not phone:
            raise ValueError("Users must have an phone number")

        user = self.model(
            phone=phone,
            email=self.normalize_email(email) if email else None,
            **extrfields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email=None, password=None, **extrafields):
        extrafields.setdefault("is_staff", True)
        extrafields.setdefault("is_active", True)
        extrafields.setdefault("is_superuser", True)
        user = self.create_user(
            phone=phone,
            email=email,
            password=password,
            **extrafields,
        )
        user.save(using=self._db)
        return user