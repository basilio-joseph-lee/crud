from rest_framework import serializers
from .models import AppointmentModel


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentModel
        fields = [
            "appointment_id",
            "guest",
            "booking",
            "room",
            "assigned_staff",
            "service_type",
            "scheduled_at",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["appointment_id", "created_at"]