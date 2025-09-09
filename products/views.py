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
from .models import Category, Unit, Product, StockMovement, StockAdjustment, StockAlert, Location, ProductLocationStock, StockTransfer
from .serializers import (
    CategorySerializer, UnitSerializer, ProductSerializer, 
    StockMovementSerializer, StockAdjustmentSerializer, StockAlertSerializer,
    ProductStockSummarySerializer, LocationSerializer, ProductLocationStockSerializer, StockTransferSerializer
)
from sales.models import SalesDetail

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

    @action(detail=False, methods=['get'])
    def valuation(self, request):
        """Valuation report using weighted average cost."""
        queryset = Product.objects.all()
        total_qty = sum([p.stock for p in queryset])
        total_value = sum([(p.average_cost or p.cost) * p.stock for p in queryset])
        items = [
            {
                'product_id': str(p.product_id),
                'name': p.name,
                'stock': p.stock,
                'average_cost': float(p.average_cost or p.cost),
                'valuation': float((p.average_cost or p.cost) * p.stock),
            } for p in queryset
        ]
        return Response({
            'total_quantity': total_qty,
            'total_valuation': total_value,
            'items': items
        })

    @action(detail=True, methods=['get'])
    def stock_history(self, request, pk=None):
        """Get stock movement history for a specific product"""
        product = self.get_object()
        movements = product.stock_movements.order_by('-created_at')
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def barcode_image(self, request, pk=None):
        """Generate a barcode PNG for the product's barcode."""
        try:
            import barcode
            from barcode.writer import ImageWriter
            from io import BytesIO
            from django.http import HttpResponse
        except ImportError:
            return Response({'detail': 'barcode package not installed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        product = self.get_object()
        code = product.barcode or product.sku or str(product.product_id)
        ean = barcode.get('code128', code, writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="{code}.png"'
        return response

    @action(detail=True, methods=['get'])
    def qrcode_image(self, request, pk=None):
        """Generate a QR code PNG for the product (encodes barcode)."""
        try:
            import qrcode
            from io import BytesIO
            from django.http import HttpResponse
        except ImportError:
            return Response({'detail': 'qrcode package not installed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        product = self.get_object()
        data = product.barcode or product.sku or str(product.product_id)
        img = qrcode.make(data)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="{data}_qr.png"'
        return response

    @action(detail=False, methods=['get'])
    def scan(self, request):
        """Lookup a product by scanned code (barcode or SKU)."""
        code = request.query_params.get('code')
        if not code:
            return Response({'detail': 'code is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(Q(barcode=code) | Q(sku=code))
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reorder_suggestions(self, request):
        """Suggest reorder quantities using average daily sales over a window and safety days.

        Query params:
        - days: lookback window in days (default 30)
        - safety_days: extra coverage days (default 7)
        - top: limit number of products (optional)
        """
        try:
            lookback_days = int(request.query_params.get('days', 30))
            safety_days = int(request.query_params.get('safety_days', 7))
        except ValueError:
            return Response({'detail': 'days and safety_days must be integers'}, status=status.HTTP_400_BAD_REQUEST)

        since = timezone.now().date() - timedelta(days=lookback_days)
        # Aggregate sales quantity per product in window
        sales = SalesDetail.objects.filter(created_at__date__gte=since).values('product').annotate(
            qty_sold=Sum('quantity')
        )
        product_to_sold = {row['product']: row['qty_sold'] or 0 for row in sales}

        suggestions = []
        for product in Product.objects.all():
            sold = float(product_to_sold.get(product.pk, 0))
            avg_daily = sold / max(lookback_days, 1)
            target_cover_days = safety_days
            # simple target stock = avg_daily * target_cover_days + minQuantity buffer
            target_stock = (avg_daily * target_cover_days) + float(product.minQuantity)
            reorder_qty = max(0, int(round(target_stock - float(product.stock))))
            if reorder_qty > 0:
                suggestions.append({
                    'product_id': str(product.product_id),
                    'name': product.name,
                    'current_stock': product.stock,
                    'min_quantity': product.minQuantity,
                    'avg_daily_sales': round(avg_daily, 2),
                    'suggested_order_qty': reorder_qty,
                })

        top_param = request.query_params.get('top')
        if top_param:
            try:
                limit = int(top_param)
                suggestions = suggestions[:limit]
            except ValueError:
                pass

        return Response({
            'window_days': lookback_days,
            'safety_days': safety_days,
            'suggestions': suggestions,
        })

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

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client']
    search_fields = ['name', 'code']

class ProductLocationStockViewSet(viewsets.ModelViewSet):
    queryset = ProductLocationStock.objects.all()
    serializer_class = ProductLocationStockSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client', 'product', 'location']
    search_fields = []

class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_client', 'product', 'from_location', 'to_location']

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        transfer = self.get_object()
        transfer.apply()
        return Response(self.get_serializer(transfer).data)
