from django.urls import path
from .views import userServices, updateDeleteUsers, LoginView

urlpatterns = [
    path('users/', userServices.as_view(), name='user-services'),
    path('users/<int:pk>/', updateDeleteUsers.as_view(), name='user-detail'),
    path('login/', LoginView.as_view(), name='login'),
]