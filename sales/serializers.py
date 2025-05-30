from rest_framework import serializers
from .models import SalesHeader, SalesDetail, Receipt
from users.models import UserClient
from registry.models import Customer, PaymentOption

class SalesHeaderSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    payment_option = serializers.PrimaryKeyRelatedField(queryset=PaymentOption.objects.all())

    class Meta:
        model = SalesHeader
        fields = '__all__'
        read_only_fields = ['sales_header_id', 'created_at', 'updated_at']
    
class SalesDetailSerializer(serializers.ModelSerializer):
    sales_header = serializers.PrimaryKeyRelatedField(queryset=SalesHeader.objects.all())
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())

    class Meta:
        model = SalesDetail
        fields = '__all__'
        read_only_fields = ['sales_detail_id', 'created_at', 'updated_at']

class ReceiptSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    payment_option = serializers.PrimaryKeyRelatedField(queryset=PaymentOption.objects.all())
    sales_header = serializers.PrimaryKeyRelatedField(queryset=SalesHeader.objects.all())

    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ['receipt_id', 'created_at', 'updated_at']
