from rest_framework import serializers
from .models import PurchaseHeader, PurchaseDetail, Payment, PurchaseOrderHeader, PurchaseOrderDetail, GRNHeader, GRNDetail
from registry.models import Supplier, PaymentOption
from products.models import Product, Unit


class PurchaseOrderItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    unit_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    price_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2)


class PurchaseOrderCreateSerializer(serializers.Serializer):
    supplier_id = serializers.UUIDField()
    expected_date = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = PurchaseOrderItemSerializer(many=True)


class PurchaseOrderConvertSerializer(serializers.Serializer):
    payment_option_id = serializers.UUIDField(required=False)
    invoice_number = serializers.CharField(required=False, allow_blank=True)


class GenerateGRNSerializer(serializers.Serializer):
    grn_number = serializers.CharField(required=True)
    
class PurchaseHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseHeader
        fields = '__all__'
        read_only_fields = ('order_number', 'invoice_number', 'created_at', 'updated_at')

class PurchaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDetail
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PurchaseOrderHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderHeader
        fields = '__all__'
        read_only_fields = ('order_number', 'created_at', 'updated_at')

class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDetail
        fields = '__all__'

class GRNHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRNHeader
        fields = '__all__'

class GRNDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRNDetail
        fields = '__all__'


class PurchaseOrderHeaderFullSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderHeader
        fields = '__all__'

    def get_details(self, obj):
        return PurchaseOrderDetailSerializer(obj.po_details.all(), many=True).data


class PurchaseHeaderFullSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseHeader
        fields = '__all__'

    def get_details(self, obj):
        return PurchaseDetailSerializer(obj.purchase_details.all(), many=True).data