from django.urls import path

from . import views

app_name = "aiops"

urlpatterns = [
    path("", views.index, name="index"),
]
