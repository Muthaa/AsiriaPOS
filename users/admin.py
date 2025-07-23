from django.contrib import admin

# Register your models here.
# from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserClient

@admin.register(UserClient)
class CustomUserAdmin(UserAdmin):
    model = UserClient
    list_display = ('client_name', 'phone_number', 'email', 'is_staff', 'is_superuser')
    search_fields = ('client_name', 'phone_number', 'email')
    ordering = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('client_name', 'phone_number', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Personal Info', {'fields': ('address',)}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('client_name', 'phone_number', 'email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
