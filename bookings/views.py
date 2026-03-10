from rest_framework import generics, filters
from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/bookings/   → list all bookings
    POST /api/bookings/   → create a new booking
    """

    serializer_class = BookingSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["status", "guest__id", "room__id"]
    ordering_fields = ["check_in_date", "check_out_date", "total_amount", "created_at"]

    def get_queryset(self):
        queryset = Booking.objects.select_related("guest", "room", "created_by").all()

        status = self.request.query_params.get("status")
        guest_id = self.request.query_params.get("guest")
        room_id = self.request.query_params.get("room")

        if status:
            queryset = queryset.filter(status=status)
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)
        if room_id:
            queryset = queryset.filter(room_id=room_id)

        return queryset


class BookingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/bookings/<booking_id>/  → retrieve a booking
    PUT    /api/bookings/<booking_id>/  → full update
    PATCH  /api/bookings/<booking_id>/  → partial update
    DELETE /api/bookings/<booking_id>/  → delete a booking
    """

    queryset = Booking.objects.select_related("guest", "room", "created_by").all()
    serializer_class = BookingSerializer
    lookup_field = "booking_id"