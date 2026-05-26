from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from .models import TransactionModel
from .serializers import TransactionSerializer
import datetime


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

        category   = self.request.query_params.get("category")
        guest_id   = self.request.query_params.get("guest")
        booking_id = self.request.query_params.get("booking")
        created_by = self.request.query_params.get("created_by")

        if category:   queryset = queryset.filter(category=category)
        if guest_id:   queryset = queryset.filter(guest_id=guest_id)
        if booking_id: queryset = queryset.filter(booking_id=booking_id)
        if created_by: queryset = queryset.filter(created_by_id=created_by)

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


class SalesSummaryView(APIView):
    """
    GET /api/sales/summary/?year=2026&month=3
    month is optional — if omitted returns full year view
    """

    def get(self, request):
        year  = int(request.query_params.get("year", datetime.date.today().year))
        month = request.query_params.get("month")

        # ── Base queryset ──
        qs = TransactionModel.objects.filter(transaction_date__year=year)
        if month:
            qs = qs.filter(transaction_date__month=int(month))

        # ── KPI stats ──
        totals = qs.aggregate(
            total_revenue=Sum("amount"),
            total_transactions=Count("transaction_id"),
            avg_transaction=Avg("amount"),
        )
        total_revenue      = float(totals["total_revenue"]      or 0)
        total_transactions = int(totals["total_transactions"]   or 0)
        avg_transaction    = float(totals["avg_transaction"]    or 0)

        # ── Revenue by category ──
        by_category_qs = (
            qs.values("category")
              .annotate(revenue=Sum("amount"), count=Count("transaction_id"))
              .order_by("-revenue")
        )
        by_category = [
            {
                "category": row["category"],
                "revenue":  float(row["revenue"] or 0),
                "count":    row["count"],
                "pct":      round(float(row["revenue"] or 0) / total_revenue * 100, 1) if total_revenue else 0,
            }
            for row in by_category_qs
        ]

        # ── Monthly revenue — always full year for chart ──
        monthly_qs = (
            TransactionModel.objects
            .filter(transaction_date__year=year)
            .annotate(month=TruncMonth("transaction_date"))
            .values("month")
            .annotate(revenue=Sum("amount"), count=Count("transaction_id"))
            .order_by("month")
        )
        monthly_map = {row["month"].month: row for row in monthly_qs}
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly = [
            {
                "month":      m,
                "month_name": month_names[m - 1],
                "revenue":    float(monthly_map[m]["revenue"] or 0) if m in monthly_map else 0,
                "count":      int(monthly_map[m]["count"]    or 0) if m in monthly_map else 0,
            }
            for m in range(1, 13)
        ]

        # ── Top rooms by revenue ──
        top_rooms_qs = (
            qs.filter(
                category=TransactionModel.Category.ROOM_BOOKINGS,
                booking__isnull=False,
            )
            .values(
                "booking__room__room_id",
                "booking__room__room_number",
                "booking__room__type",
            )
            .annotate(revenue=Sum("amount"), bookings=Count("booking_id", distinct=True))
            .order_by("-revenue")[:5]
        )
        top_rooms = [
            {
                "room_id":     row["booking__room__room_id"],
                "room_number": row["booking__room__room_number"],
                "type":        row["booking__room__type"],
                "revenue":     float(row["revenue"] or 0),
                "bookings":    row["bookings"],
            }
            for row in top_rooms_qs
        ]

        # ── Top services by usage (excludes Room Bookings) ──
        top_services_qs = (
            qs.exclude(category=TransactionModel.Category.ROOM_BOOKINGS)
              .values("category")
              .annotate(revenue=Sum("amount"), count=Count("transaction_id"))
              .order_by("-count")
        )
        top_services = [
            {
                "category": row["category"],
                "revenue":  float(row["revenue"] or 0),
                "count":    row["count"],
            }
            for row in top_services_qs
        ]

        return Response({
            "filters": {
                "year":  year,
                "month": int(month) if month else None,
            },
            "kpi": {
                "total_revenue":      total_revenue,
                "total_transactions": total_transactions,
                "avg_transaction":    round(avg_transaction, 2),
            },
            "by_category":  by_category,
            "monthly":      monthly,
            "top_rooms":    top_rooms,
            "top_services": top_services,
        })