from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserChangeForm, UserCreationForm
from .models import User
# Register your models here.
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["phone", "email"]
    # list_filter = ["is_admin"]
    fieldsets = [
        ("Personal info", {"fields": ["phone", "first_name", "last_name", "email", "profile"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser"]}),
        ("Groups & Permissions", {"fields": ["groups", "user_permissions"]}),
        ("Login information", {"fields": ["last_login"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        ("Personal info", {"fields": ["phone", "first_name", "last_name", "email", "profile"]}),
        ("password",{"fields": ["password1", "password2"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser"]}),
        ("Groups & Permissions", {"fields": ["groups", "user_permissions"]}),

        # (
        #     None,
        #     {
        #         "classes": ["wide"],
        #         "fields": ["phone", "email", "password1", "password2"],
        #     },
        # ),
    ]
    search_fields = ["phone"]
    ordering = ["phone"]
    filter_horizontal = []


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
