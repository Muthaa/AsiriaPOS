from django.db import models
from users.models import UserClient
from products.models import Product, Unit, Category
from registry.models import Customer, PaymentOption

class SalesHeader(models.Model):
    sales_header_id = models.AutoField(primary_key=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=255, unique=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale Header {self.order_number} by {self.user_client.username}"

class SalesDetail(models.Model):
    sales_detail_id = models.AutoField(primary_key=True)
    sales_header = models.ForeignKey(SalesHeader, on_delete=models.CASCADE, related_name='sales_details')
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale Detail {self.sales_detail_id} for {self.product.name}"
    
class Receipt(models.Model):
    receipt_id = models.AutoField(primary_key=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE)
    sales_header = models.ForeignKey(SalesHeader, on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=255, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    narration = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Receipt {self.receipt_number} for Sale {self.sales_header.order_number}"