from rest_framework import serializers
from .models import PurchaseHeader, PurchaseDetail, Payment
    
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