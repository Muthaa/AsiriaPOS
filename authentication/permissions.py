from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Owner'

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['Owner', 'Manager']

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['Owner', 'Manager', 'Employee']
