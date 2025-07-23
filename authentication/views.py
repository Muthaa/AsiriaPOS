from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import update_last_login
from Domain.models import CustomToken
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.models import UserClient

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT Token Obtain Pair View with enhanced Swagger documentation
    """
    
    @swagger_auto_schema(
        operation_description="Obtain JWT access and refresh tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone_number', 'password'],
            properties={
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User phone number',
                    example='0712345678'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User password',
                    example='string'
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully authenticated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='JWT access token'
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='JWT refresh token'
                        ),
                        'user_client_id': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='User client ID'
                        ),
                        'storename': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Store name'
                        ),
                        'client_name': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Client name'
                        ),
                        'role': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='User role (first group)'
                        ),
                    }
                ),
                examples={
                    'application/json': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user_client_id': 'uuid-string-here',
                        'storename': 'My Store',
                        'client_name': 'John Doe',
                        'role': 'Owner'
                    }
                }
            ),
            401: openapi.Response(
                description="Invalid credentials",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Error message'
                        ),
                    }
                ),
                examples={
                    'application/json': {
                        'detail': 'No active account found with the given credentials'
                    }
                }
            ),
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and response.data.get('access'):
            # Get user details from the access token
            access_token = response.data['access']
            token = AccessToken(access_token)
            user_id = token['user_id'] if 'user_id' in token else None
            
            # If using custom claim, adjust accordingly
            if not user_id and 'user_client_id' in token:
                user_id = token['user_client_id']
            
            # Add user_client_id to response
            response.data['user_client_id'] = user_id
            
            try:
                # Get the user object
                user = UserClient.objects.get(user_client_id=user_id)
                
                # Add store name and client name
                response.data['storename'] = user.storename
                response.data['client_name'] = user.client_name
                
                # Add first group (role)
                first_group = user.groups.first()
                response.data['role'] = first_group.name if first_group else None
                
            except UserClient.DoesNotExist:
                # If user not found, still return the token but without extra info
                pass
                
        return response

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT Token Refresh View with enhanced Swagger documentation
    """
    
    @swagger_auto_schema(
        operation_description="Refresh JWT access token using refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='JWT refresh token',
                    example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully refreshed token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='New JWT access token'
                        ),
                    }
                ),
                examples={
                    'application/json': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            ),
            401: openapi.Response(
                description="Invalid refresh token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Error message'
                        ),
                    }
                ),
                examples={
                    'application/json': {
                        'detail': 'Token is invalid or expired'
                    }
                }
            ),
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow login without token

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        device_name = request.data.get("device_name", "Unknown Device")
        user = authenticate(phone_number=phone_number, password=password)

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

class CustomLogoutView(APIView):
    """
    Custom Logout View with enhanced Swagger documentation
    """
    
    @swagger_auto_schema(
        operation_description="Logout user by blacklisting refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='JWT refresh token to blacklist',
                    example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Success message'
                        ),
                    }
                ),
                examples={
                    'application/json': {
                        'message': 'Logged out successfully'
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid token or token already blacklisted",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Error message'
                        ),
                    }
                ),
                examples={
                    'application/json': {
                        'error': 'Invalid token or token already blacklisted'
                    }
                }
            ),
        },
        tags=['Authentication']
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # This requires SimpleJWT's blacklist app to be enabled and migrated
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token or token already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
