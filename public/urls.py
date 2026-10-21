from django.urls import path

from . import views

app_name = "public"

urlpatterns = [
    path("", views.home, name="home"),
    path("providers/", views.provider_list, name="provider_list"),
    path("providers/<slug:slug>/", views.provider_detail, name="provider_detail"),
    path("locations/", views.location_list, name="location_list"),
    path("locations/<slug:slug>/", views.location_detail, name="location_detail"),
    path("insurance/", views.insurance_list, name="insurance"),
    path("patient-resources/", views.resource_list, name="resource_list"),
    path("patient-resources/<slug:slug>/", views.resource_detail, name="resource_detail"),
    path("request-appointment/", views.request_appointment, name="request_appointment"),
    path("request-appointment/received/", views.request_thanks, name="request_thanks"),
]
