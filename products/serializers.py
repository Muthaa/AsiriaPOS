from rest_framework import serializers
from .models import Category, Unit, Product, StockMovement, StockAdjustment, StockAlert, Location, ProductLocationStock, StockTransfer
from users.models import UserClient


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())
    # user_client = serializers.PrimaryKeyRelatedField(
    #     queryset=UserClient.objects.all(),
    #     pk_field=serializers.UUIDField(format='hex_verbose')
    # )
    class Meta:
        model = Unit
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)
    stock_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    average_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'
        read_only_fields = ('movement_id', 'previous_stock', 'new_stock', 'created_at')

class StockAdjustmentSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    adjustment_type_display = serializers.CharField(source='get_adjustment_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = StockAdjustment
        fields = '__all__'
        read_only_fields = ('adjustment_id', 'created_at', 'approved_at', 'is_approved', 'approved_by')

class StockAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = '__all__'
        read_only_fields = ('alert_id', 'created_at', 'resolved_at', 'resolved_by')

class ProductStockSummarySerializer(serializers.ModelSerializer):
    """Serializer for product stock summary with movement history"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)
    stock_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    recent_movements = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_recent_movements(self, obj):
        """Get recent stock movements for the product"""
        movements = obj.stock_movements.order_by('-created_at')[:10]
        return StockMovementSerializer(movements, many=True).data

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ProductLocationStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLocationStock
        fields = '__all__'

class StockTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransfer
        fields = '__all__'
        read_only_fields = ['transfer_id', 'created_at']