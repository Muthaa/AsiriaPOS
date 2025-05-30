from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import viewsets
from .models import PurchaseHeader, PurchaseDetail, Payment
from .serializers import PurchaseHeaderSerializer, PurchaseDetailSerializer, PaymentSerializer
from authentication.permissions import IsOwner, IsManager, IsEmployee
from rest_framework.permissions import IsAuthenticated

@swagger_auto_schema(tags=["Purchases"])
class PurchaseHeaderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseHeader.objects.all()
    serializer_class = PurchaseHeaderSerializer
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view

class PurchaseDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseDetail.objects.all()
    serializer_class = PurchaseDetailSerializer
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view