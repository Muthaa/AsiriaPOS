from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from AsiriaPOS.mixins import SwaggerTagMixin  # Import SwaggerTagMixin

# Create your views here.
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers import UserClientSerializer, PasswordResetTokenSerializer, UserClientManagerSerializer
from .models import UserClient, PasswordResetToken, UserClientManager  # Import your custom user models

class UserClientViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = UserClient.objects.all()
    serializer_class = UserClientSerializer
    # permission_classes = [permissions.IsAuthenticated]
    swagger_tag = "Clients"

class PasswordResetTokenViewSet(viewsets.ModelViewSet):
    queryset = PasswordResetToken.objects.all()
    serializer_class = PasswordResetTokenSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust permissions as needed
    # You can add custom logic here if needed  
    