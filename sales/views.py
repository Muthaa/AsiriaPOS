from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import viewsets
from .models import SalesHeader, SalesDetail, Receipt
from .serializers import SalesHeaderSerializer, SalesDetailSerializer, ReceiptSerializer
from authentication.permissions import IsOwner, IsManager, IsEmployee
from rest_framework.permissions import IsAuthenticated
from AsiriaPOS.mixins import SwaggerTagMixin

class SalesHeaderViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesHeader.objects.all()
    serializer_class = SalesHeaderSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

class SalesDetailViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesDetail.objects.all()
    serializer_class = SalesDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

class ReceiptViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"
    