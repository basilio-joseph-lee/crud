from django.db import models


class AppointmentModel(models.Model):
    class ServiceType(models.TextChoices):
        CHECK_IN = "Check-in", "Check-in"
        CHECK_OUT = "Check-out", "Check-out"
        SPA_SESSION = "Spa Session", "Spa Session"
        DINING = "Dining", "Dining"
        OTHER = "Other", "Other"

    class Status(models.TextChoices):
        CONFIRMED = "Confirmed", "Confirmed"
        PENDING = "Pending", "Pending"
        CANCELLED = "Cancelled", "Cancelled"
        COMPLETED = "Completed", "Completed"

    appointment_id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(
        "guests.GuestModel",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    room = models.ForeignKey(
        "rooms.RoomModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    scheduled_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    assigned_staff = models.ForeignKey(
        "users.UserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_appointments",
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"Appointment {self.appointment_id} — {self.service_type} ({self.status})"