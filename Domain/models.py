# Create your models here.
from django.conf import settings
from django.db import models
from rest_framework.authtoken.models import Token
from django.db.models import JSONField

class CustomToken(Token):  # Extend the default DRF Token model
    device_name = models.CharField(max_length=255, null=True, blank=True)  # Store device info
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_name}"


class AuditLog(models.Model):
    """Generic audit log for sensitive actions."""
    ACTION_CHOICES = [
        ('PRICE_OVERRIDE', 'Price Override'),
        ('VOID', 'Void'),
        ('REFUND', 'Refund'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    audit_log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=128)
    object_id = models.CharField(max_length=128)
    reason = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    before_data = JSONField(null=True, blank=True)
    after_data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} {self.model_name}#{self.object_id} by {self.user_id}"
