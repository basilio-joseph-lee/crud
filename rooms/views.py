from rest_framework import generics
from .models import RoomModel
from .serializers import RoomSerializer

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = RoomModel.objects.all()
    serializer_class = RoomSerializer

class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomModel.objects.all()
    serializer_class = RoomSerializer