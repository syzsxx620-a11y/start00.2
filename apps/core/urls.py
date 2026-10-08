from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("set-currency/", views.set_currency, name="set_currency"),
]
