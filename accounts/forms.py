from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Otp, Address, Province, City


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
        user.set_password(self.cleaned_data.get("password1"))
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
    code = forms.CharField(max_length=4, min_length=4, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Code"}))

    def clean(self):
        cleaned_data=super().clean()
        data = self.cleaned_data.get("code")
        if not data.isdigit():
            raise ValidationError("your code must be number")
        elif len(data) != 4:
            raise ValidationError("your code must have 4 character!")
        return cleaned_data
class AddressForm(forms.ModelForm):
    province = forms.ModelChoiceField(queryset=Province.objects.all(), widget=forms.Select(attrs={'class':'custom-select'}))
    city = forms.ModelChoiceField(queryset=City.objects.all(), widget=forms.Select(attrs={'class':'custom-select'}))
    class Meta:
        model = Address
        exclude = ["user"]
        widgets = {
            'full_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class':'form-ckeck'}),
            
        }
        labels = {
            "is_default":"Make address default: "
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["city"].queryset = City.objects.none()

        if "province" in self.data:
            try:
                province_id = int(self.data.get("province"))
                self.fields["city"].queryset = City.objects.filter(
                    province_id=province_id
                )
            except (TypeError, ValueError):
                pass

        elif self.instance.pk:
            self.fields["province"].initial = self.instance.city.province
            self.fields["city"].queryset = City.objects.filter(
                province=self.instance.city.province
            )
    def clean(self):
        cleaned_data = super().clean()
        city = cleaned_data.get("city")
        province = cleaned_data.get("province")
        if not city.province.id == province.id:
            raise ValidationError("city and province does not blong together")
        return cleaned_data

class ProfileEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].disabled = True
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "profile",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "profile": forms.FileInput(attrs={
                "class": "form-control profile-input",
            }),
        }