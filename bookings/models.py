from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "Confirmed", "Confirmed"
        PENDING = "Pending", "Pending"
        CANCELLED = "Cancelled", "Cancelled"
        COMPLETED = "Completed", "Completed"

    booking_id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(
        "guests.GuestModel",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    room = models.ForeignKey(
        "rooms.RoomModel",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        "users.UserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_bookings",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking {self.booking_id} — {self.guest} ({self.status})"