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
    path("auth/change-phone/", views.ChangePhoneView.as_view(), name="change_phone"),
    path("auth/change-phone/verify/", views.VerifyChangePhoneView.as_view(), name="verify_change_phone"),
    path("auth/change-phone/resend-code/", views.ResendOtpChangePhoneView.as_view(), name="resend_code_change_phone"),
    path('addresses/add/', views.AddAddressView.as_view(), name="add_address"),
    path('cities/<int:pk>/', views.get_cities, name="get_cities"),
    path('addresses/edit/<int:pk>/', views.AddressEditView.as_view(), name="edit_address"),
    path('addresses/', views.AddressListView.as_view(), name="addresses_list"),
    path('addresses/delete/<int:pk>/', views.AddressDeleteView.as_view(),name="delete_address"),  
    path('addresses/set-default/<int:pk>', views.set_default_address, name="set_default_address"),
    path('profile/', views.ProfileView.as_view(), name="user_profile"),
    path('profile/edit/', views.ProfileEditView.as_view(), name="profile_edit"),
    path('', views.DashboardView.as_view(), name="dashboard"),
]
