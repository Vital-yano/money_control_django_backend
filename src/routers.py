from django.urls import path, include


urlpatterns = [path("user/", include("src.main.urls"))]
