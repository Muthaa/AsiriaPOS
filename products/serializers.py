from rest_framework import serializers
from .models import Product, Category, Unit
from users.models import UserClient


class ProductSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'sku': {'required': False, 'allow_blank': True},
            'barcode': {'required': False, 'allow_blank': True},
        }
        # fields = ['id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at']

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