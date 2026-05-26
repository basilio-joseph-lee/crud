from django.urls import path
from .views import (
    RoomListCreateView,
    RoomRetrieveUpdateDestroyView,
    RoomOccupancyTodayView,
    RoomStatusUpdateView,
)

urlpatterns = [
    path("rooms/",                          RoomListCreateView.as_view()),
    path("rooms/<int:room_id>/",            RoomRetrieveUpdateDestroyView.as_view()),
    path("rooms/occupancy/today/",          RoomOccupancyTodayView.as_view()),
    path("rooms/<int:room_id>/room-status/", RoomStatusUpdateView.as_view()),
]