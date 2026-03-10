from rest_framework import generics, filters
from .models import AppointmentModel
from .serializers import AppointmentSerializer


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/appointments/   → list all appointments
    POST /api/appointments/   → create a new appointment
    """

    serializer_class = AppointmentSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["status", "service_type"]
    ordering_fields = ["scheduled_at", "created_at", "status"]

    def get_queryset(self):
        queryset = AppointmentModel.objects.select_related(
            "guest", "booking", "room", "assigned_staff"
        ).all()

        status = self.request.query_params.get("status")
        service_type = self.request.query_params.get("service_type")
        guest_id = self.request.query_params.get("guest")

        if status:
            queryset = queryset.filter(status=status)
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)

        return queryset


class AppointmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/appointments/<appointment_id>/  → retrieve
    PUT    /api/appointments/<appointment_id>/  → full update
    PATCH  /api/appointments/<appointment_id>/  → partial update
    DELETE /api/appointments/<appointment_id>/  → delete
    """

    queryset = AppointmentModel.objects.select_related(
        "guest", "booking", "room", "assigned_staff"
    ).all()
    serializer_class = AppointmentSerializer
    lookup_field = "appointment_id"