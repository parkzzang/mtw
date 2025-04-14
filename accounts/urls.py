# accounts/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("send_code/", views.send_code_view, name="send_code"),
    path("verify_code/", views.verify_code_view, name="verify_code"),
    path('check-username/', views.check_username_view, name='check_username'),
    path('verify/', views.verify_view, name='verify'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify/reset/", views.reset_verification, name="reset_verification"),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]
