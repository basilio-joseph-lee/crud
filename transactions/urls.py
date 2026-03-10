from django.urls import path
from .views import TransactionListCreateView, TransactionRetrieveUpdateDestroyView

urlpatterns = [
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list-create"),
    path(
        "transactions/<int:transaction_id>/",
        TransactionRetrieveUpdateDestroyView.as_view(),
        name="transaction-detail",
    ),
]