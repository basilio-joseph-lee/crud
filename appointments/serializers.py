from rest_framework import serializers
from .models import AppointmentModel


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentModel
        fields = [
            "appointment_id",
            "guest",
            "booking",
            "service_type",
            "room",
            "scheduled_at",
            "status",
            "assigned_staff",
            "notes",
            "created_at",
        ]
        read_only_fields = ["appointment_id", "created_at"]