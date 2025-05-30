from django.contrib import admin

# Register your models here.
# from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserClient

@admin.register(UserClient)
class CustomUserAdmin(UserAdmin):
    model = UserClient
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
