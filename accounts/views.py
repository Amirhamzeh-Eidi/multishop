from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import FormView, CreateView, UpdateView, ListView, DeleteView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from . import forms
from . import models
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
import secrets
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
        otp = models.Otp(identifier=form.cleaned_data.get("phone"), code=str(secrets.randbelow(9000)+1000))
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
            if next_url:
                return redirect(reverse("accounts:user_authentication") + f"?next={next_url}")
            return redirect("accounts:user_authentication")
    def get(self, request):
        return redirect("accounts:user_authentication")

class VerifyCodeView(FormView):
    form_class = forms.VerifyCodeForm
    template_name = "accounts/verify_code.html"
    def form_valid(self, form):
        try:
            otp = services.OtpService.verify(token=self.request.GET.get("token"), code=form.cleaned_data.get("code"))
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

class AddAddressView(LoginRequiredMixin, CreateView):
    model = models.Address
    form_class = forms.AddressForm
    template_name = 'accounts/add_address.html'
    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("accounts:addresses_list")
    def form_valid(self, form):
        address = form.save(commit=False)
        user = self.request.user
        address.user = user
        if models.Address.objects.filter(user=user).count() >=5:
            form.add_error(None, ValidationError("you can create 5 address in maximum", code="address_count_limit"))
            return self.form_invalid(form)
        if address.is_default:
            models.Address.objects.filter(user=address.user, is_default=True).update(is_default=False)
            address.save()
        return super().form_valid(form)
def get_cities(request, pk):
    cities = models.City.objects.filter(province_id=pk).values("id", "name")
    return JsonResponse(
        list(cities),
        safe=False
    )

class AddressEditView(LoginRequiredMixin, UpdateView):
    form_class = forms.AddressForm
    template_name = 'accounts/edit_address.html'
    success_url = reverse_lazy("accounts:addresses_list")
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user
        if address.is_default:
            models.Address.objects.filter(user=address.user, is_default=True).update(is_default=False)
            address.save()
        return super().form_valid(form)
    model = models.Address

class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy("accounts:addresses_list")
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class ChangePhoneView(LoginRequiredMixin, FormView):
    form_class = forms.UserAuthForm
    template_name = "accounts/change_phone.html"
    def form_valid(self, form):
        if models.User.objects.filter(phone=form.cleaned_data.get("phone")).exists():
            form.add_error("phone", ValidationError("this phone already exist."))
            return self.form_invalid(form)
        otp = models.Otp(identifier=form.cleaned_data.get("phone"), code=str(secrets.randbelow(9000)+1000))
        print(otp.code)
        otp.save()
        next_url = self.request.POST.get("next")
        if next_url:
            return redirect(reverse("accounts:verify_change_phone") + f"?token={otp.token}&next={next_url}")
        else:
            return redirect(reverse("accounts:verify_change_phone") + f"?token={otp.token}")

class VerifyChangePhoneView(LoginRequiredMixin, FormView):
    form_class = forms.VerifyCodeForm
    template_name = "accounts/verify_change_phone.html"
    def form_valid(self, form):
        try:
            otp = services.OtpService.verify(token=self.request.GET.get("token"), code=form.cleaned_data.get("code"))
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
            form.add_error("code", ValidationError("this phone already exist."))
            return self.form_invalid(form)
        except models.User.DoesNotExist:
            user = self.request.user
            user.phone = phone
            user.save()
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

class ResendOtpChangePhoneView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            otp = services.OtpService.resend_otp(token=request.POST.get("token"))
            print(otp.code)
            return redirect(reverse("accounts:verify_change_phone") + f"?token={otp.token}")
        except services.OtpRequestToSoon:
            messages.error(request, "you must wait for 1 minute for send new code", extra_tags="otp-too-soon")
            return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}")
        except services.OtpShortTermLimitExceeded:
            messages.error(request, "you can ask 3 code in 10 minutes", extra_tags="otp-short-limit")
            return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}")
        except services.OtpDailyLimitExceeded:
            messages.error(request, "you can ask 20 code in 24 houres", extra_tags="otp-daily-limit")
            return redirect(reverse("accounts:verify_code") + f"?token={request.POST.get('token')}")
        except services.InvalidOtpError:
            return redirect("accounts:verify_change_phone")
    def get(self, request):
        return redirect("accounts:user_authentication")

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
@login_required
def set_default_address(request, pk):
    address = get_object_or_404(models.Address, id=pk, user=request.user)
    models.Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    return redirect("accounts:addresses_list")