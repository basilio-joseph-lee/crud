from django.db import models

class RoomModel(models.Model):
    class RoomType(models.TextChoices):
        STANDARD = 'Standard', 'Standard'
        DELUXE = 'Deluxe', 'Deluxe'
        SUITE = 'Suite', 'Suite'

    class RoomStatus(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        OCCUPIED = 'Occupied', 'Occupied'
        HOUSEKEEPING = 'Housekeeping', 'Housekeeping'
        MAINTENANCE = 'Maintenance', 'Maintenance'

    room_id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField()
    type = models.CharField(max_length=10, choices=RoomType.choices)
    status = models.CharField(max_length=12, choices=RoomStatus.choices)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rooms'

    def __str__(self):
        return f'Room {self.room_number}'