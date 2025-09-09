from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SalesHeader, SalesDetail, Receipt, CashSession, SalesPayment, SalesReturn, SalesRefund, SalesReservation
from .serializers import SalesHeaderSerializer, SalesDetailSerializer, ReceiptSerializer, CashSessionSerializer, SalesPaymentSerializer, SalesReturnSerializer, SalesRefundSerializer, SalesReservationSerializer
from authentication.permissions import IsOwner, IsManager, IsEmployee, CanApproveRefunds, CanVoidTransactions, CanOverridePrices
from rest_framework.permissions import IsAuthenticated
from AsiriaPOS.mixins import SwaggerTagMixin
from Domain.models import AuditLog
from datetime import datetime
from django.utils import timezone

class SalesHeaderViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesHeader.objects.all()
    serializer_class = SalesHeaderSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        header = self.get_object()
        if header.status != 'PENDING':
            return Response({'detail': 'Only pending orders can be confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        header.status = 'CONFIRMED'
        header.save()
        # Release reservations tied to this order
        SalesReservation.objects.filter(sales_header=header, is_active=True).update(is_active=False)
        return Response(self.get_serializer(header).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        header = self.get_object()
        if header.status == 'CANCELLED':
            return Response({'detail': 'Already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        header.status = 'CANCELLED'
        header.save()
        # Remove reservations to free stock
        SalesReservation.objects.filter(sales_header=header, is_active=True).update(is_active=False)
        return Response(self.get_serializer(header).data)

class SalesDetailViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesDetail.objects.all()
    serializer_class = SalesDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee, CanVoidTransactions]
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

    @action(detail=False, methods=['get'])
    def margin_report(self, request):
        """Sales margin report using product average cost, filterable by date range."""
        qs = self.get_queryset()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        total_revenue = 0.0
        total_cogs = 0.0
        by_product = {}

        for d in qs.select_related('product'):
            revenue = float(d.price_per_unit) * d.quantity
            cost_unit = float(getattr(d.product, 'average_cost', 0) or float(d.product.cost))
            cogs = cost_unit * d.quantity
            total_revenue += revenue
            total_cogs += cogs
            key = str(d.product.product_id)
            if key not in by_product:
                by_product[key] = {
                    'product_id': key,
                    'name': d.product.name,
                    'quantity': 0,
                    'revenue': 0.0,
                    'cogs': 0.0,
                }
            by_product[key]['quantity'] += d.quantity
            by_product[key]['revenue'] += revenue
            by_product[key]['cogs'] += cogs

        items = []
        for v in by_product.values():
            v['margin'] = v['revenue'] - v['cogs']
            v['margin_percent'] = (v['margin'] / v['revenue'] * 100.0) if v['revenue'] else 0.0
            items.append(v)

        return Response({
            'total_revenue': total_revenue,
            'total_cogs': total_cogs,
            'total_margin': total_revenue - total_cogs,
            'margin_percent': ((total_revenue - total_cogs) / total_revenue * 100.0) if total_revenue else 0.0,
            'items': items,
        })

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """Reserve stock for this sales line if the order is pending."""
        detail = self.get_object()
        header = detail.sales_header
        if header.status != 'PENDING':
            return Response({'detail': 'Reservation allowed only for pending orders'}, status=status.HTTP_400_BAD_REQUEST)
        # Ensure enough free stock (stock - active reservations)
        from django.db.models import Sum
        active_reserved = SalesReservation.objects.filter(product=detail.product, is_active=True).aggregate(q=Sum('quantity'))['q'] or 0
        free_stock = max(0, detail.product.stock - active_reserved)
        if free_stock < detail.quantity:
            return Response({'detail': f'Insufficient free stock to reserve. Free: {free_stock}'}, status=status.HTTP_400_BAD_REQUEST)
        exp_days = request.data.get('expiry_days')
        expiry_at = None
        try:
            if exp_days is not None:
                expiry_at = timezone.now() + timezone.timedelta(days=int(exp_days))
        except Exception:
            expiry_at = None
        SalesReservation.objects.create(
            user_client=detail.user_client,
            sales_header=header,
            sales_detail=detail,
            product=detail.product,
            quantity=detail.quantity,
            expiry_at=expiry_at,
        )
        return Response({'detail': 'Reserved'}, status=status.HTTP_201_CREATED)

class ReceiptViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='CREATE',
            model_name='Receipt',
            object_id=str(instance.receipt_id),
            reason='Receipt created',
            before_data=None,
            after_data={'sales_header': str(instance.sales_header_id), 'amount_paid': float(instance.amount_paid)}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='Receipt',
            object_id=str(instance.receipt_id),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'sales_header': str(instance.sales_header_id), 'amount_paid': float(instance.amount_paid)},
            after_data=None
        )
        return response

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveRefunds])
    def approve(self, request, pk=None):
        instance = self.get_object()
        instance.approve(request.user)
        return Response(self.get_serializer(instance).data)

class SalesRefundViewSet(SwaggerTagMixin, viewsets.ModelViewSet):
    queryset = SalesRefund.objects.all()
    serializer_class = SalesRefundSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveRefunds])
    def approve(self, request, pk=None):
        instance = self.get_object()
        instance.approve(request.user)
        return Response(self.get_serializer(instance).data)

class SalesReservationViewSet(SwaggerTagMixin, viewsets.ReadOnlyModelViewSet):
    queryset = SalesReservation.objects.all()
    serializer_class = SalesReservationSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsManager | IsEmployee]
    swagger_tag = "Sales"
    filterset_fields = ['user_client', 'sales_header', 'product', 'is_active']
    