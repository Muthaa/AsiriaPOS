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
    supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseHeader
        fields = '__all__'
        read_only_fields = ('order_number', 'invoice_number', 'created_at', 'updated_at')

    def get_supplier_name(self, obj):
        return getattr(obj.supplier, 'name', None)

class PurchaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDetail
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PurchaseOrderHeaderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderHeader
        fields = '__all__'
        read_only_fields = ('order_number', 'created_at', 'updated_at')

    def get_supplier_name(self, obj):
        return getattr(obj.supplier, 'name', None)

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
    supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderHeader
        fields = '__all__'

    def get_details(self, obj):
        return PurchaseOrderDetailSerializer(obj.po_details.all(), many=True).data

    def get_supplier_name(self, obj):
        return getattr(obj.supplier, 'name', None)


class PurchaseHeaderFullSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseHeader
        fields = '__all__'

    def get_details(self, obj):
        return PurchaseDetailSerializer(obj.purchase_details.all(), many=True).data

    def get_supplier_name(self, obj):
        return getattr(obj.supplier, 'name', None)


class PurchaseOrderFullUpdateDetailSerializer(serializers.Serializer):
    po_detail_id = serializers.UUIDField(required=False)
    product_id = serializers.UUIDField(required=False)
    unit_id = serializers.UUIDField(required=False)
    quantity = serializers.IntegerField(min_value=1, required=False)
    price_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    delete = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        if data.get('delete'):
            # Only po_detail_id is required for delete
            if not data.get('po_detail_id'):
                raise serializers.ValidationError({'po_detail_id': 'This field is required for deletion.'})
            return data
        # For non-delete, require quantity and price_per_unit
        if 'quantity' not in data:
            raise serializers.ValidationError({'quantity': ['This field is required.']})
        if 'price_per_unit' not in data:
            raise serializers.ValidationError({'price_per_unit': ['This field is required.']})
        return data

class PurchaseOrderFullUpdateSerializer(serializers.Serializer):
    expected_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    details = PurchaseOrderFullUpdateDetailSerializer(many=True)

class PurchaseFullUpdateDetailSerializer(serializers.Serializer):
    purchase_detail_id = serializers.UUIDField(required=False)
    product_id = serializers.UUIDField(required=False)
    unit_id = serializers.UUIDField(required=False)
    quantity = serializers.IntegerField(min_value=1)
    price_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    delete = serializers.BooleanField(required=False, default=False)

class PurchaseFullUpdateSerializer(serializers.Serializer):
    payment_option_id = serializers.UUIDField(required=False)
    invoice_number = serializers.CharField(required=False, allow_blank=True)
    details = PurchaseFullUpdateDetailSerializer(many=True)