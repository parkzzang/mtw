from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("index/", views.index_view, name="index"),
    path("mypage/", views.mypage_view, name="mypage"),
]