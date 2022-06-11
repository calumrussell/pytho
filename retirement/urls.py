from django.urls import path, include, re_path
from django.conf import settings
from django.contrib.staticfiles import views

urlpatterns = [
    path("api/", include("api.urls")),
    path("", include("front.urls")),
]
