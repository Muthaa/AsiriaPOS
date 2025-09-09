from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SalesHeader, SalesDetail, Receipt, CashSession, SalesPayment, SalesReturn, SalesRefund
from .serializers import SalesHeaderSerializer, SalesDetailSerializer, ReceiptSerializer, CashSessionSerializer, SalesPaymentSerializer, SalesReturnSerializer, SalesRefundSerializer
from authentication.permissions import IsOwner, IsManager, IsEmployee
from rest_framework.permissions import IsAuthenticated
from AsiriaPOS.mixins import SwaggerTagMixin
from Domain.models import AuditLog

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='SalesDetail',
            object_id=str(instance.pk),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'product': str(instance.product_id), 'quantity': instance.quantity}
        )
        return response

class ReceiptViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

class CashSessionViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = CashSession.objects.all()
    serializer_class = CashSessionSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        session = self.get_object()
        closing_total = request.data.get('closing_total', 0)
        session.close(request.user, closing_total)
        return Response(self.get_serializer(session).data)

class SalesPaymentViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

    @action(detail=False, methods=['post'])
    def split(self, request):
        """Create multiple payments for a sale (split payments)."""
        sales_header_id = request.data.get('sales_header')
        payments = request.data.get('payments', [])
        session_id = request.data.get('session')

        created = []
        for p in payments:
            sp = SalesPayment.objects.create(
                user_client=request.user,
                sales_header_id=sales_header_id,
                session_id=session_id,
                method=p['method'],
                amount=p['amount'],
                reference=p.get('reference')
            )
            created.append(SalesPaymentSerializer(sp).data)
        return Response(created, status=status.HTTP_201_CREATED)

class SalesReturnViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesReturn.objects.all()
    serializer_class = SalesReturnSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

class SalesRefundViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesRefund.objects.all()
    serializer_class = SalesRefundSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"
    