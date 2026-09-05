from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Otp


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['phone', 'email', 'first_name', 'last_name', 'profile']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):


    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = "__all__"


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=13, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Phone number"}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Password"}))


class UserAuthForm(forms.Form):
    phone = forms.CharField(max_length=13, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Phone number"}))

    
class VerifyCodeForm(forms.Form):
    code = forms.CharField(max_length=13, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Code"}))

    def clean(self):
        cleaned_data=super().clean()
        data = self.cleaned_data["code"]
        if not data.isdigit():
            raise ValidationError("your code must be number")
        elif len(data) != 4:
            raise ValidationError("your code must have 4 character!")
        return cleaned_data
