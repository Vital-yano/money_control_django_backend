from django.urls import path
from . import views


urlpatterns = [
    path("create", views.CreateUserView.as_view()),
    path("send_code", views.SendCodeView.as_view()),
]
