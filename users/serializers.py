from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

from .models import UserClient, PasswordResetToken, UserClientManager  # Import your custom user models

class UserClientManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserClientManager
        fields ='__all__'


class UserClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserClient
        # Specify the fields you want to include in the serializer
        fields = '__all__'  # Include all fields in the serializer
        # fields = ['user_client_id', 'username', 'password', 'phone_number', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'is_admin', 'is_superuser', 'last_login']
        # Exclude password from the serialized output
        # read_only_fields = ['password']
        # write_only_fields = ['password']  # Make password write-only
        extra_kwargs = {'password': {'write_only': True}}

class PasswordResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetToken
        # Specify the fields you want to include in the serializer or Include all fields in the serializer 
        fields = '__all__'    
