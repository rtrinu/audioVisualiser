from django.urls import path
from . import views

app_name = "spotify"

urlpatterns = [
    path("login", views.login, name="login"),
    path("callback", views.callback, name="callback"),
    path("refresh_token", views.refresh_token, name="refresh_token"),
]
