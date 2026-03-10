from rest_framework import serializers
from .models import GuestModel

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestModel
        fields = '__all__'
        read_only_fields = ['id', 'created_at']