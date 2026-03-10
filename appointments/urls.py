from django.urls import path
from .views import AppointmentListCreateView, AppointmentRetrieveUpdateDestroyView

urlpatterns = [
    path("appointments/", AppointmentListCreateView.as_view(), name="appointment-list-create"),
    path(
        "appointments/<int:appointment_id>/",
        AppointmentRetrieveUpdateDestroyView.as_view(),
        name="appointment-detail",
    ),
]