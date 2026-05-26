from django.urls import path
from .views import (
    TransactionListCreateView,
    TransactionRetrieveUpdateDestroyView,
    SalesSummaryView,
)

urlpatterns = [
    path(
        "transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "transactions/<int:transaction_id>/",
        TransactionRetrieveUpdateDestroyView.as_view(),
        name="transaction-detail",
    ),
    path(
        "sales/summary/",
        SalesSummaryView.as_view(),
        name="sales-summary",
    ),
]