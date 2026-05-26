from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  # ✅ add JSONParser
from django.contrib.auth.hashers import check_password
from .models import UserModel
from .serializers import userSerializer


class userServices(generics.ListCreateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = userSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser] 


class updateDeleteUsers(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserModel.objects.all()
    serializer_class = userSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'message': 'Login successful',
            'user': userSerializer(user, context={'request': request}).data
        }, status=status.HTTP_200_OK)