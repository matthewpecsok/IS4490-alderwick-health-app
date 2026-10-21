from django.urls import path

from . import views

app_name = "devtools"

urlpatterns = [
    path("gemini/", views.gemini_check, name="gemini_check"),
]
