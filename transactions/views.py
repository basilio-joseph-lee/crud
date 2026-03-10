from rest_framework import generics, filters
from .models import TransactionModel
from .serializers import TransactionSerializer


class TransactionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/transactions/   → list all transactions
    POST /api/transactions/   → create a new transaction
    """

    serializer_class = TransactionSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["category", "guest__full_name"]
    ordering_fields = ["transaction_date", "amount", "created_at"]

    def get_queryset(self):
        queryset = TransactionModel.objects.select_related(
            "booking", "guest", "created_by"
        ).all()

        category = self.request.query_params.get("category")
        guest_id = self.request.query_params.get("guest")
        booking_id = self.request.query_params.get("booking")

        if category:
            queryset = queryset.filter(category=category)
        if guest_id:
            queryset = queryset.filter(guest_id=guest_id)
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)

        return queryset


class TransactionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/transactions/<transaction_id>/  → retrieve
    PUT    /api/transactions/<transaction_id>/  → full update
    PATCH  /api/transactions/<transaction_id>/  → partial update
    DELETE /api/transactions/<transaction_id>/  → delete
    """

    queryset = TransactionModel.objects.select_related(
        "booking", "guest", "created_by"
    ).all()
    serializer_class = TransactionSerializer
    lookup_field = "transaction_id"