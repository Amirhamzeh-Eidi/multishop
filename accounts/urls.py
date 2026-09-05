from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = "accounts"
urlpatterns = [
    path("login/", views.UserLoginView.as_view(),name="user_login"),
    path("logout/", LogoutView.as_view(next_page="home:home"),name="user_logout"),
]
