from django.urls import path

from . import views

app_name = "clinician"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("schedule/", views.schedule, name="schedule"),
    path("patients/", views.patient_list, name="patients"),
    path("patients/<int:pk>/", views.chart, name="chart"),
    path("visits/<int:pk>/", views.visit_detail, name="visit_detail"),
    path("visits/<int:pk>/edit/", views.edit_note, name="edit_note"),
    path("appointments/<int:appointment_pk>/note/", views.start_note, name="start_note"),
    path("inbox/", views.inbox, name="inbox"),
    path("inbox/<int:pk>/", views.thread_detail, name="thread"),
]
