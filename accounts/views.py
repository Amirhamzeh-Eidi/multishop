from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views import View
from . import forms
from . import models
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from random import randint
from django.urls import reverse
from . import services
from django.contrib import messages
from django.core.exceptions import ValidationError

# Create your views here.


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = forms.UserLoginForm
    redirect_authenticated_user = True
    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return next_url
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
        next_url = self.request.POST.get("next")
        otp.save()
        if next_url:
            return redirect(reverse("accounts:verify_code") + f"?token={otp.token}&next={next_url}")
        else:
            return redirect(reverse("accounts:verify_code") + f"?token={otp.token}")
class ResendOtpView(View):
    def post(self, request):
        next_url = self.request.POST.get("next")
        try:
            otp = services.OtpService.resend_otp(token=request.POST.get("token"))
            print("token: " + request.POST.get("token"))
            print(otp.code)
            if next_url:
                return redirect(reverse("accounts:verify_code") + f"?token={otp.token}&next={next_url}")
            else:
                return redirect(reverse("accounts:verify_code") + f"?token={otp.token}")
        except services.OtpRequestToSoon:
            messages.error(request, "you must wait for 1 minute for send new code", extra_tags="otp-too-soon")
            if next_url:
                return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}&next={next_url}")
            return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}")
        except services.OtpShortTermLimitExceeded:
            messages.error(request, "you can ask 3 code in 10 minutes", extra_tags="otp-short-limit")
            if next_url:
                return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}&next={next_url}")
            return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}")
        except services.OtpDailyLimitExceeded:
            messages.error(request, "you can ask 20 code in 24 houres", extra_tags="otp-daily-limit")
            if next_url:
                return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}&next={next_url}")
            return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}")
        except services.InvalidOtpError:
            print("token: " + request.POST.get("token"))
            if next_url:
                return redirect(reverse("accounts:user_authentication" + f"?next={next_url}"))
            return redirect("accounts:user_authentication")
    def get(self, request):
        return redirect("accounts:user_authentication")

class VerifyCodeView(FormView):
    form_class = forms.VerifyCodeForm
    template_name = "accounts/verify_code.html"
    def form_valid(self, form):
        try:
            otp = services.OtpService.verify(token=self.request.GET.get("token"), code=form.cleaned_data["code"])
        except services.InvalidOtpError:
            form.add_error("code", ValidationError("you dont have active code, send code again!", code="invalid_otp"))
            return self.form_invalid(form)
        except services.ExpiredOtpError:
            form.add_error("code", ValidationError("your code expired", code="expired_code"))
            return self.form_invalid(form)
        except services.ToManyAttemptsError:
            form.add_error("code", ValidationError("to many attemts.", code="to_many_attempts"))
            return self.form_invalid(form)
        except services.WrongOtpError:
            form.add_error("code", ValidationError("your code is wrong", code="wrong_code"))
            return self.form_invalid(form)
        phone = otp.identifier
        try:
            user = models.User.objects.get(phone=phone)
        except models.User.DoesNotExist:
            user = models.User.objects.create_user(phone=phone)
            user.save()
        login(self.request, user)
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(reverse("home:home"))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["invalid_otp"] = form.has_error(
            "code", 
            "invalid_otp"
        )
        context["expired_code"] = form.has_error(
            "code", 
            "expired_code"
        )
        context["to_many_attempts"] = form.has_error(
            "code", 
            "to_many_attempts"
        )
        context["wrong_code"] = form.has_error(
            "code", 
            "wrong_code"
        )
        return context
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)
