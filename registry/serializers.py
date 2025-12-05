from rest_framework import serializers
from .models import Customer, Supplier, PaymentOption, ExpenseCategory, Expense, BusinessProfile, AnonymousProfile
from users.models import UserClient

class CustomerSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class SupplierSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())

    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PaymentOptionSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())

    class Meta:
        model = PaymentOption
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ExpenseCategorySerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())
    
    class Meta:
        model = ExpenseCategory 
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ExpenseSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())
    expense_category = serializers.PrimaryKeyRelatedField(queryset=ExpenseCategory.objects.all())
    payment_option = serializers.PrimaryKeyRelatedField(queryset=PaymentOption.objects.all())

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class BusinessProfileSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())

    class Meta:
        model = BusinessProfile
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AnonymousProfileSerializer(serializers.ModelSerializer):
    user_client = serializers.PrimaryKeyRelatedField(queryset=UserClient.objects.all())

    class Meta:
        model = AnonymousProfile
        fields = '__all__'
        read_only_fields = ('first_seen', 'last_seen')