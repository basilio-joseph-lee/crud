
from django.db import models

class GuestModel(models.Model):
    guest_id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(
        'users.UserModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id'
    )
    full_name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    id_type = models.CharField(max_length=50, null=True, blank=True)
    id_number = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'guests'

    def __str__(self):
        return self.full_name