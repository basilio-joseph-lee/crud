from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "guest",
            "room",
            "check_in_date",
            "check_out_date",
            "status",
            "total_amount",
            "notes",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["booking_id", "created_at"]

    def validate(self, data):
        check_in = data.get("check_in_date")
        check_out = data.get("check_out_date")
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                {"check_out_date": "Check-out date must be after check-in date."}
            )
        return data