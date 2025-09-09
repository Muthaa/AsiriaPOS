from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import PurchaseHeader, PurchaseDetail, Payment, PurchaseOrderHeader, PurchaseOrderDetail, GRNHeader, GRNDetail
from .serializers import PurchaseHeaderSerializer, PurchaseDetailSerializer, PaymentSerializer, PurchaseOrderHeaderSerializer, PurchaseOrderDetailSerializer, GRNHeaderSerializer, GRNDetailSerializer
from Domain.models import AuditLog
from authentication.permissions import IsOwner, IsManager, IsEmployee
from rest_framework.permissions import IsAuthenticated

@swagger_auto_schema(tags=["Purchases"])
class PurchaseHeaderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseHeader.objects.all()
    serializer_class = PurchaseHeaderSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='PurchaseHeader',
            object_id=str(instance.purchase_header_id),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'invoice_number': instance.invoice_number, 'total_cost': float(instance.total_cost)},
            after_data=None
        )
        return response
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view

class PurchaseDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseDetail.objects.all()
    serializer_class = PurchaseDetailSerializer
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PurchaseOrderHeaderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderHeader.objects.all()
    serializer_class = PurchaseOrderHeaderSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='CREATE',
            model_name='PurchaseOrderHeader',
            object_id=str(instance.po_header_id),
            reason='PO created',
            before_data=None,
            after_data={'order_number': instance.order_number, 'supplier': str(instance.supplier_id)}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='PurchaseOrderHeader',
            object_id=str(instance.po_header_id),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'order_number': instance.order_number},
            after_data=None
        )
        return response

class PurchaseOrderDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderDetail.objects.all()
    serializer_class = PurchaseOrderDetailSerializer

class GRNHeaderViewSet(viewsets.ModelViewSet):
    queryset = GRNHeader.objects.all()
    serializer_class = GRNHeaderSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='CREATE',
            model_name='GRNHeader',
            object_id=str(instance.grn_header_id),
            reason='GRN created',
            before_data=None,
            after_data={'grn_number': instance.grn_number, 'supplier': str(instance.supplier_id)}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='GRNHeader',
            object_id=str(instance.grn_header_id),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'grn_number': instance.grn_number},
            after_data=None
        )
        return response

class GRNDetailViewSet(viewsets.ModelViewSet):
    queryset = GRNDetail.objects.all()
    serializer_class = GRNDetailSerializer
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view