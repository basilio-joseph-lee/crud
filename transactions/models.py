from django.db import models


class TransactionModel(models.Model):
    class Category(models.TextChoices):
        ROOM_BOOKINGS = "Room Bookings", "Room Bookings"
        SPA_WELLNESS = "Spa & Wellness", "Spa & Wellness"
        DINING = "Dining", "Dining"
        OTHERS = "Others", "Others"

    transaction_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    guest = models.ForeignKey(
        "guests.GuestModel",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    transaction_date = models.DateField()
    created_by = models.ForeignKey(
        "users.UserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transaction {self.transaction_id} — {self.category} ({self.amount})"