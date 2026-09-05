from django.urls import reverse_lazy
from . import forms
from django.contrib.auth.views import LoginView

# Create your views here.


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = forms.UserLoginForm
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy("home:home")
