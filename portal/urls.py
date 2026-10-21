from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("appointments/", views.appointments, name="appointments"),
    path("appointments/<int:pk>/cancel/", views.cancel_appointment, name="cancel_appointment"),
    path("appointments/request/", views.request_appointment, name="request_appointment"),
    path("health-record/", views.health_summary, name="health_summary"),
    path("health-record/test-results/", views.lab_results, name="lab_results"),
    path("health-record/visits/", views.visits, name="visits"),
    path("health-record/visits/<int:pk>/", views.visit_detail, name="visit_detail"),
    path("messages/", views.message_list, name="messages"),
    path("messages/new/", views.new_message, name="new_message"),
    path("messages/<int:pk>/", views.thread_detail, name="thread"),
    path("profile/", views.profile, name="profile"),
]
