from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Customer, Supplier, PaymentOption, ExpenseCategory, Expense, BusinessProfile
from .serializers import CustomerSerializer, SupplierSerializer, PaymentOptionSerializer, ExpenseCategorySerializer, ExpenseSerializer, BusinessProfileSerializer

@swagger_auto_schema(tags=["Registry"])
# Create your views here.
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]  

class PaymentOptionViewSet(viewsets.ModelViewSet):
    queryset = PaymentOption.objects.all()
    serializer_class = PaymentOptionSerializer
    permission_classes = [IsAuthenticated]

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()    
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

class BusinessProfile(viewsets.ModelViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]
