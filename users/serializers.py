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
        fields = [
            'user_client_id', 'storename', 'client_name', 'phone_number', 'email',
            'password', 'address', 'consumer_key', 'consumer_secret',
            'is_active', 'date_joined', 'last_login'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'user_client_id': {'read_only': True},
        }

    def create(self, validated_data):
        from django.contrib.auth.models import Group
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        # Assign to 'Owner' group
        owner_group, created = Group.objects.get_or_create(name='Owner')
        user.groups.add(owner_group)
        return user

class PasswordResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetToken
        # Specify the fields you want to include in the serializer or Include all fields in the serializer 
        fields = '__all__'    
