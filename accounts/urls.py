# accounts/urls.py
from django.urls import path
from .views import signup_view, send_code_view, verify_code_view

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("send_code/", send_code_view, name="send_code"),
    path("verify_code/", verify_code_view, name="verify_code"),
]
