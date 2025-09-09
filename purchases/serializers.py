from rest_framework import serializers
from .models import PurchaseHeader, PurchaseDetail, Payment, PurchaseOrderHeader, PurchaseOrderDetail, GRNHeader, GRNDetail
    
class PurchaseHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseHeader
        fields = '__all__'

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