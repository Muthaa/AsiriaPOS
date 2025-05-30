from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import update_last_login
from Domain.models import CustomToken
from rest_framework import status

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow login without token

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        device_name = request.data.get("device_name", "Unknown Device")
        user = authenticate(username=username, password=password)

        if user:
            # Delete old tokens if any (Enforce one active session per user)
            CustomToken.objects.filter(user=user).delete()

            # Generate new token
            token = CustomToken.objects.create(user=user, device_name=device_name)
            token.save()

            # Update last login timestamp
            update_last_login(None, user)  # Update last login timestamp

            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        user = request.user
        if user.is_authenticated:
            CustomToken.objects.filter(user=user).delete()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
