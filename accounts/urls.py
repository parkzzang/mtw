# accounts/urls.py
from django.urls import path
from .views import signup_view, send_code_view, verify_code_view, check_username_view, verify_view

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("send_code/", send_code_view, name="send_code"),
    path("verify_code/", verify_code_view, name="verify_code"),
    path('check-username/', check_username_view, name='check_username'),
    path('verify/', verify_view, name='verify'),
]
