from rest_framework import serializers
from .models import TransactionModel


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionModel
        fields = [
            "transaction_id",
            "booking",
            "guest",
            "category",
            "amount",
            "description",
            "transaction_date",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["transaction_id", "created_at"]