from django.urls import path
from .views import GuestListCreateView, GuestRetrieveUpdateDestroyView

urlpatterns = [
    path('guests/', GuestListCreateView.as_view(), name='guest-list-create'),
    path('guests/<int:pk>/', GuestRetrieveUpdateDestroyView.as_view(), name='guest-detail'),
]