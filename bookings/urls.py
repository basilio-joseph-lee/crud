from django.urls import path
from .views import BookingListCreateView, BookingRetrieveUpdateDestroyView, BookingMonthlyAnalyticsView

urlpatterns = [
    path("bookings/", BookingListCreateView.as_view(), name="booking-list-create"),
    path(
        "bookings/<int:booking_id>/",
        BookingRetrieveUpdateDestroyView.as_view(),
        name="booking-detail",
    ),
    path("bookings/analytics/monthly", BookingMonthlyAnalyticsView.as_view()),
]