from rest_framework import serializers
from .models import SalesHeader, SalesDetail, Receipt, CashSession, SalesPayment, SalesReturn, SalesRefund
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

class CashSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashSession
        fields = '__all__'
        read_only_fields = ['session_id', 'opened_at', 'closed_at', 'status']

class SalesPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPayment
        fields = '__all__'
        read_only_fields = ['sales_payment_id', 'created_at']

class SalesReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReturn
        fields = '__all__'
        read_only_fields = ['sales_return_id', 'created_at']

class SalesRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRefund
        fields = '__all__'
        read_only_fields = ['refund_id', 'created_at']
