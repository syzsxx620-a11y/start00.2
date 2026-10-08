from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("confirmation/<str:order_number>/", views.confirmation, name="confirmation"),
    path("track/", views.order_track, name="track"),
    path("history/", views.order_history, name="history"),
    path("<str:order_number>/<str:email>/", views.order_detail, name="detail"),
]
