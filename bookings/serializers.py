from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "guest",
            "room",
            "created_by",
            "check_in_date",
            "check_out_date",
            "status",
            "room_status",
            "total_amount",
            "notes",
            "created_at",
        ]
        read_only_fields = ["booking_id", "created_at"]

    def validate(self, data):
        check_in  = data.get("check_in_date")
        check_out = data.get("check_out_date")

        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                {"check_out_date": "Check-out date must be after check-in date."}
            )
        return data

    def create(self, validated_data):
        # Auto-compute total_amount if not provided or if staff didn't override
        room      = validated_data.get("room")
        check_in  = validated_data.get("check_in_date")
        check_out = validated_data.get("check_out_date")

        if room and check_in and check_out:
            nights = (check_out - check_in).days
            # Only auto-compute if total_amount not manually provided
            if not validated_data.get("total_amount"):
                validated_data["total_amount"] = room.price_per_night * nights

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If dates or room changed, recompute total_amount unless staff overrode it
        room      = validated_data.get("room", instance.room)
        check_in  = validated_data.get("check_in_date", instance.check_in_date)
        check_out = validated_data.get("check_out_date", instance.check_out_date)

        if "total_amount" not in validated_data:
            nights = (check_out - check_in).days
            validated_data["total_amount"] = room.price_per_night * nights

        return super().update(instance, validated_data)