from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Owner').exists()

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Owner', 'Manager']).exists()

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Owner', 'Manager', 'Employee']).exists()

class CanApproveRefunds(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Owner', 'Manager']).exists()

class CanVoidTransactions(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Owner', 'Manager']).exists()

class CanOverridePrices(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Owner', 'Manager']).exists()