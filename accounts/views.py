from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from . import forms
from . import models
from django.contrib.auth.views import LoginView
from random import randint
from django.urls import reverse

# Create your views here.


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = forms.UserLoginForm
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy("home:home")
class UserAuthView(FormView):
    form_class = forms.UserAuthForm
    template_name = "accounts/auth.html"
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        otp = models.Otp(identifier=form.cleaned_data["phone"], code=randint(1000, 9999))
        print(otp.code)
        otp.save()
        return redirect(reverse("accounts:verify_code") + f"?token={otp.token}")
