from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = "accounts"
urlpatterns = [
    path("login/", views.UserLoginView.as_view(),name="user_login"),
    path("logout/", LogoutView.as_view(next_page="home:home"),name="user_logout"),
    path("auth/", views.UserAuthView.as_view(),name="user_authentication"),
    path("auth/verify/", views.VerifyCodeView.as_view(),name="verify_code"),
    path("auth/resend-code/", views.ResendOtpView.as_view(), name="resend_code"),
    path('addresses/add/', views.AddAddressView.as_view(), name="add_address"),
    path('cities/<int:pk>/', views.get_cities, name="get_cities"),
    path('addresses/edit/<int:pk>/', views.AddressEditView.as_view(), name="edit_address"),
    path('addresses/', views.AddressListView.as_view(), name="addresses_list")
]
