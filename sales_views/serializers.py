from rest_framework import serializers


class CheckoutItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    unit_id = serializers.UUIDField(required=False)
    qty = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


class CheckoutInitializeSerializer(serializers.Serializer):
    items = CheckoutItemSerializer(many=True)
    payment_method = serializers.ChoiceField(choices=['CASH', 'CARD', 'MOBILE', 'CREDIT', 'OTHER'])
    payment_option_id = serializers.UUIDField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    mpesa_token = serializers.CharField(required=False, allow_blank=True)
    card_token = serializers.CharField(required=False, allow_blank=True)
    credit_account_code = serializers.CharField(required=False, allow_blank=True)
    terminal_id = serializers.CharField(required=False, allow_blank=True)


class ReceiptLinkSerializer(serializers.Serializer):
    receipt_id = serializers.UUIDField()
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
