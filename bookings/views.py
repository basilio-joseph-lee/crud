import calendar
from datetime import datetime, timezone
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, DurationField, Q
from django.db.models.functions import TruncMonth
from .models import Booking
from rooms.models import RoomModel
from transactions.models import TransactionModel
from appointments.models import AppointmentModel
from .serializers import BookingSerializer


def create_room_booking_transaction(booking):
    """Auto-create Room Bookings transaction when booking is confirmed."""
    already_exists = TransactionModel.objects.filter(
        booking=booking,
        category=TransactionModel.Category.ROOM_BOOKINGS,
    ).exists()

    if not already_exists:
        nights = (booking.check_out_date - booking.check_in_date).days
        TransactionModel.objects.create(
            booking=booking,
            guest=booking.guest,
            category=TransactionModel.Category.ROOM_BOOKINGS,
            amount=booking.total_amount,
            description=f"Room {booking.room.room_number} — {nights} night{'s' if nights > 1 else ''}",
            transaction_date=datetime.now(timezone.utc).date(),
            created_by=booking.created_by,
        )


def create_checkout_appointment(booking):
    """Auto-create Check-out appointment when booking is completed."""
    already_exists = AppointmentModel.objects.filter(
        booking=booking,
        service_type=AppointmentModel.ServiceType.CHECK_OUT,
    ).exists()

    if not already_exists:
        AppointmentModel.objects.create(
            booking=booking,
            guest=booking.guest,
            room=booking.room,
            service_type=AppointmentModel.ServiceType.CHECK_OUT,
            scheduled_at=datetime.now(timezone.utc),
            status=AppointmentModel.Status.COMPLETED,
            assigned_staff=booking.created_by,
            notes=f"Auto check-out for Booking #{booking.booking_id}",
        )


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

        status   = self.request.query_params.get("status")
        guest_id = self.request.query_params.get("guest")
        room_id  = self.request.query_params.get("room")
        created_by = self.request.query_params.get("created_by")

        if status:
            queryset = queryset.filter(status=status)
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if created_by:                                          
            queryset = queryset.filter(created_by=created_by)

        return queryset

    def perform_create(self, serializer):
        booking = serializer.save()

        if booking.status == Booking.Status.CONFIRMED:
            booking.room_status = Booking.RoomStatus.OCCUPIED
            booking.save(update_fields=["room_status"])
            create_room_booking_transaction(booking)

        elif booking.status == Booking.Status.PENDING:
            booking.room_status = Booking.RoomStatus.AVAILABLE
            booking.save(update_fields=["room_status"])


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

    def perform_update(self, serializer):
        old_status = self.get_object().status
        booking    = serializer.save()
        new_status = booking.status

        if old_status != new_status:

            if new_status == Booking.Status.CONFIRMED:
                booking.room_status = Booking.RoomStatus.OCCUPIED
                booking.save(update_fields=["room_status"])
                create_room_booking_transaction(booking)

            elif new_status == Booking.Status.COMPLETED:
                booking.room_status = Booking.RoomStatus.HOUSEKEEPING
                booking.save(update_fields=["room_status"])
                create_checkout_appointment(booking)   # ← auto checkout

            elif new_status == Booking.Status.CANCELLED:
                booking.room_status = Booking.RoomStatus.AVAILABLE
                booking.save(update_fields=["room_status"])


class BookingMonthlyAnalyticsView(APIView):
    """
    GET /api/bookings/analytics/monthly/
    """

    def get(self, request):
        year   = request.query_params.get("year")
        status = request.query_params.get("status")

        queryset = Booking.objects.all()

        if status:
            queryset = queryset.filter(status=status)
        if year:
            queryset = queryset.filter(check_in_date__year=year)

        total_rooms = RoomModel.objects.count()

        results = (
            queryset
            .annotate(period=TruncMonth("check_in_date"))
            .values("period")
            .annotate(
                total_bookings          = Count("booking_id"),
                total_revenue           = Sum("total_amount"),
                avg_revenue_per_booking = Avg("total_amount"),
                total_room_nights       = Sum(
                    ExpressionWrapper(
                        F("check_out_date") - F("check_in_date"),
                        output_field=DurationField()
                    )
                ),
                unique_guests      = Count("guest", distinct=True),
                confirmed_count    = Count("booking_id", filter=Q(status="Confirmed")),
                pending_count      = Count("booking_id", filter=Q(status="Pending")),
                cancelled_count    = Count("booking_id", filter=Q(status="Cancelled")),
                total_transactions = Count("transactions", distinct=True),
                total_appointments = Count("appointments", distinct=True),
            )
            .order_by("period")
        )

        data = []
        for row in results:
            period                = row["period"]
            days_in_month         = calendar.monthrange(period.year, period.month)[1]
            available_room_nights = total_rooms * days_in_month

            booked_nights = row["total_room_nights"]
            if booked_nights is None:
                booked_nights = 0
            elif hasattr(booked_nights, "days"):
                booked_nights = booked_nights.days

            occupancy_rate = (
                round((booked_nights / available_room_nights) * 100, 2)
                if available_room_nights > 0 else 0
            )
            revpar = (
                round(float(row["total_revenue"] or 0) / available_room_nights, 2)
                if available_room_nights > 0 else 0
            )
            avg_length_of_stay = (
                round(booked_nights / row["total_bookings"], 2)
                if row["total_bookings"] > 0 else 0
            )
            cancellation_rate = (
                round((row["cancelled_count"] / row["total_bookings"]) * 100, 2)
                if row["total_bookings"] > 0 else 0
            )

            data.append({
                "period":                  period,
                "total_bookings":          row["total_bookings"],
                "unique_guests":           row["unique_guests"],
                "total_revenue":           row["total_revenue"],
                "avg_revenue_per_booking": round(float(row["avg_revenue_per_booking"] or 0), 2),
                "revpar":                  revpar,
                "booked_nights":           booked_nights,
                "available_room_nights":   available_room_nights,
                "avg_length_of_stay":      avg_length_of_stay,
                "occupancy_rate":          f"{occupancy_rate}%",
                "status_breakdown": {
                    "confirmed":  row["confirmed_count"],
                    "pending":    row["pending_count"],
                    "cancelled":  row["cancelled_count"],
                },
                "cancellation_rate":   f"{cancellation_rate}%",
                "total_transactions":  row["total_transactions"],
                "total_appointments":  row["total_appointments"],
            })

        return Response({
            "total_rooms": total_rooms,
            "filters":     {"year": year, "status": status},
            "results":     data,
        })