# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from rest_framework.authtoken.models import Token

class CustomToken(Token):  # Extend the default DRF Token model
    device_name = models.CharField(max_length=255, null=True, blank=True)  # Store device info
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_name}"
