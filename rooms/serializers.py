from rest_framework import serializers
from .models import RoomModel

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomModel
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']