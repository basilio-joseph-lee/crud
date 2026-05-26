from datetime import date
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RoomModel
from .serializers import RoomSerializer
from bookings.models import Booking


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = RoomModel.objects.all()
    serializer_class = RoomSerializer


class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomModel.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "room_id"


class RoomStatusUpdateView(APIView):
    """
    PATCH /api/rooms/<room_id>/room-status/
    """
    def patch(self, request, room_id):
        new_room_status = request.data.get("room_status")
        valid = [choice[0] for choice in Booking.RoomStatus.choices]

        if not new_room_status or new_room_status not in valid:
            return Response(
                {"error": f"Invalid room_status. Choose from: {valid}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking = (
            Booking.objects
            .filter(room_id=room_id)
            .exclude(status=Booking.Status.CANCELLED)
            .order_by("-created_at")
            .first()
        )

        if not booking:
            return Response(
                {"error": "No active booking found for this room."},
                status=status.HTTP_404_NOT_FOUND,
            )

        booking.room_status = new_room_status
        booking.save(update_fields=["room_status"])

        return Response({
            "room_id":     room_id,
            "booking_id":  booking.booking_id,
            "room_status": booking.room_status,
            "updated":     True,
        })


class RoomOccupancyTodayView(APIView):
    """
    GET /api/rooms/occupancy/today/
    """
    def get(self, request):
        today = date.today()

        # Active bookings overlapping today
        active_bookings = Booking.objects.filter(
            check_in_date__lte=today,
            check_out_date__gte=today,
        ).select_related("guest", "room").exclude(
            status=Booking.Status.CANCELLED
        )

        # Completed bookings from today still in housekeeping/maintenance
        completed_today = Booking.objects.filter(
            check_out_date=today,
            status=Booking.Status.COMPLETED,
            room_status__in=[
                Booking.RoomStatus.HOUSEKEEPING,
                Booking.RoomStatus.MAINTENANCE,
            ]
        ).select_related("guest", "room")

        # Merge — active bookings take priority over completed
        occupied_rooms: dict = {b.room_id: b for b in completed_today}
        for b in active_bookings:
            occupied_rooms[b.room_id] = b

        # Checking in / out counts
        checking_in_today = Booking.objects.filter(
            check_in_date=today,
            status=Booking.Status.CONFIRMED,
        ).count()

        checking_out_today = Booking.objects.filter(
            check_out_date=today,
            status=Booking.Status.CONFIRMED,
        ).count()

        rooms = RoomModel.objects.all()
        data  = []

        for room in rooms:
            booking = occupied_rooms.get(room.room_id)

            if booking is None:
                checked_out_today = Booking.objects.filter(
                    room_id=room.room_id,
                    check_out_date=today,
                    status=Booking.Status.COMPLETED,
                ).exists()
                room_status = "Checked Out" if checked_out_today else "Vacant"

            elif booking.status == Booking.Status.COMPLETED:
                rs = booking.room_status
                if rs == Booking.RoomStatus.HOUSEKEEPING:
                    room_status = "Housekeeping"
                elif rs == Booking.RoomStatus.MAINTENANCE:
                    room_status = "Maintenance"
                else:
                    room_status = "Checked Out"

            elif booking.status == Booking.Status.CONFIRMED:
                rs = booking.room_status
                if rs == Booking.RoomStatus.HOUSEKEEPING:
                    room_status = "Housekeeping"
                elif rs == Booking.RoomStatus.MAINTENANCE:
                    room_status = "Maintenance"
                else:
                    room_status = "Occupied"

            elif booking.status == Booking.Status.PENDING:
                room_status = "Pending"

            else:
                room_status = "Vacant"

            # Next upcoming booking for vacant rooms
            next_booking = None
            if room_status == "Vacant":
                nb = (
                    Booking.objects
                    .filter(
                        room_id=room.room_id,
                        check_in_date__gt=today,
                        status=Booking.Status.CONFIRMED,
                    )
                    .select_related("guest")
                    .order_by("check_in_date")
                    .first()
                )
                if nb:
                    next_booking = {
                        "booking_id": nb.booking_id,
                        "guest_name": nb.guest.full_name,
                        "check_in":   nb.check_in_date,
                        "check_out":  nb.check_out_date,
                    }

            data.append({
                "room_id":         room.room_id,
                "room_number":     room.room_number,
                "floor":           room.floor,
                "type":            room.type,
                "price_per_night": room.price_per_night,
                "max_occupancy":   room.max_occupancy,
                "image_url":       room.image_url,
                "room_status":     room_status,
                "next_booking":    next_booking,
                "booking": {
                    "booking_id":       booking.booking_id,
                    "room_status":      booking.room_status,
                    "check_in":         booking.check_in_date,
                    "check_out":        booking.check_out_date,
                    "nights_remaining": max((booking.check_out_date - today).days, 0),
                    "guest": {
                        "guest_id": booking.guest.guest_id,
                        "name":     booking.guest.full_name,
                        "email":    booking.guest.email,
                        "phone":    booking.guest.phone,
                    },
                } if booking else None,
            })

        summary = {
            "date":               str(today),
            "total_rooms":        len(data),
            "occupied":           sum(1 for r in data if r["room_status"] == "Occupied"),
            "vacant":             sum(1 for r in data if r["room_status"] == "Vacant"),
            "pending":            sum(1 for r in data if r["room_status"] == "Pending"),
            "housekeeping":       sum(1 for r in data if r["room_status"] == "Housekeeping"),
            "maintenance":        sum(1 for r in data if r["room_status"] == "Maintenance"),
            "checked_out":        sum(1 for r in data if r["room_status"] == "Checked Out"),
            "checking_in_today":  checking_in_today,
            "checking_out_today": checking_out_today,
        }

        return Response({"summary": summary, "rooms": data})