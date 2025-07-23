from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from AsiriaPOS.mixins import SwaggerTagMixin  # Import SwaggerTagMixin
from rest_framework.permissions import AllowAny, IsAuthenticated

# Create your views here.
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers import UserClientSerializer, PasswordResetTokenSerializer, UserClientManagerSerializer
from .models import UserClient, PasswordResetToken, UserClientManager  # Import your custom user models

class UserClientViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = UserClient.objects.all()
    serializer_class = UserClientSerializer
    swagger_tag = "Clients"

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

class PasswordResetTokenViewSet(viewsets.ModelViewSet):
    queryset = PasswordResetToken.objects.all()
    serializer_class = PasswordResetTokenSerializer
    permission_classes = [permissions.IsAuthenticated]  # Adjust permissions as needed
    # You can add custom logic here if needed  
    