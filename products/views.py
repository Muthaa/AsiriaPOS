from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Category, Unit, Product, StockMovement, StockAdjustment, StockAlert
from .serializers import (
    CategorySerializer, UnitSerializer, ProductSerializer, 
    StockMovementSerializer, StockAdjustmentSerializer, StockAlertSerializer,
    ProductStockSummarySerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client']
    search_fields = ['name', 'description']

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client']
    search_fields = ['unit_name', 'description']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client', 'category', 'unit']
    search_fields = ['name', 'sku', 'barcode', 'description']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        from django.db import models
        products = Product.objects.filter(stock__lte=models.F('minQuantity'))
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get products that are out of stock"""
        products = Product.objects.filter(stock__lte=0)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stock_summary(self, request):
        """Get stock summary with movement history"""
        products = Product.objects.all()
        serializer = ProductStockSummarySerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stock_history(self, request, pk=None):
        """Get stock movement history for a specific product"""
        product = self.get_object()
        movements = product.stock_movements.order_by('-created_at')
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client', 'product', 'movement_type']
    search_fields = ['reference_number', 'reason']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get stock movement summary"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        summary = {
            'total_movements': queryset.count(),
            'total_in': queryset.filter(quantity__gt=0).aggregate(total=Sum('quantity'))['total'] or 0,
            'total_out': abs(queryset.filter(quantity__lt=0).aggregate(total=Sum('quantity'))['total'] or 0),
            'movements_by_type': queryset.values('movement_type').annotate(
                count=Count('movement_id'),
                total_quantity=Sum('quantity')
            ),
            'recent_movements': StockMovementSerializer(queryset[:10], many=True).data
        }
        
        return Response(summary)

class StockAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustment.objects.all()
    serializer_class = StockAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client', 'product', 'adjustment_type', 'is_approved']
    search_fields = ['reference_number', 'reason']
    ordering_fields = ['created_at', 'quantity_adjusted']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a stock adjustment"""
        adjustment = self.get_object()
        if adjustment.is_approved:
            return Response(
                {'error': 'Adjustment already approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the user who is approving (from request)
        approved_by = request.user
        adjustment.approve(approved_by)
        
        serializer = self.get_serializer(adjustment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending stock adjustments"""
        adjustments = StockAdjustment.objects.filter(is_approved=False)
        serializer = self.get_serializer(adjustments, many=True)
        return Response(serializer.data)

class StockAlertViewSet(viewsets.ModelViewSet):
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client', 'product', 'alert_type', 'is_active']
    search_fields = ['message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a stock alert"""
        alert = self.get_object()
        if not alert.is_active:
            return Response(
                {'error': 'Alert already resolved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the user who is resolving (from request)
        resolved_by = request.user
        alert.resolve(resolved_by)
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active stock alerts"""
        alerts = StockAlert.objects.filter(is_active=True)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get stock alert summary"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary = {
            'total_alerts': queryset.count(),
            'active_alerts': queryset.filter(is_active=True).count(),
            'resolved_alerts': queryset.filter(is_active=False).count(),
            'alerts_by_type': queryset.values('alert_type').annotate(
                count=Count('alert_id'),
                active_count=Count('alert_id', filter=Q(is_active=True))
            ),
            'recent_alerts': StockAlertSerializer(queryset[:10], many=True).data
        }
        
        return Response(summary)
