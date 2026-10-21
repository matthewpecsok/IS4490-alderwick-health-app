from django.urls import path

from . import views

app_name = "frontdesk"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("requests/", views.request_list, name="requests"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/action/", views.request_action, name="request_action"),
    path("schedule/", views.schedule, name="schedule"),
    path("appointments/<int:pk>/action/", views.appointment_action, name="appointment_action"),
    path("messages/", views.message_list, name="messages"),
    path("messages/<int:pk>/", views.thread_detail, name="thread"),
    path("patients/", views.patient_search, name="patient_search"),
    path("patients/<int:pk>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:pk>/book/", views.book_for_patient, name="book_for_patient"),
]
