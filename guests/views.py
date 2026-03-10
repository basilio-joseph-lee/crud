from rest_framework import generics
from .models import GuestModel
from .serializers import GuestSerializer

class GuestListCreateView(generics.ListCreateAPIView):
    queryset = GuestModel.objects.all()
    serializer_class = GuestSerializer

class GuestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GuestModel.objects.all()
    serializer_class = GuestSerializer