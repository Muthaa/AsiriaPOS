from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['audit_log_id', 'action', 'model_name', 'object_id', 'user', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['model_name', 'object_id', 'user__username', 'reason']

# Register your models here.
