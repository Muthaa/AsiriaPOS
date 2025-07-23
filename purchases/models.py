import uuid
from django.db import models
from products.models import Product, Unit
from users.models import UserClient
from registry.models import Supplier, PaymentOption
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class PurchaseHeader(models.Model):
    purchase_header_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='purchase_headers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_headers')
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE, related_name='purchase_headers')
    purchase_date = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=255, unique=True)
    invoice_number = models.CharField(max_length=255)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')

    def __str__(self):
        return f"Purchase Header {self.supplier.name} - {self.invoice_number} - {self.total_cost}"
 
class PurchaseDetail(models.Model):
    purchase_detail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='purchase_details')
    purchase_header = models.ForeignKey(PurchaseHeader, on_delete=models.CASCADE, related_name='purchase_details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_details')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='purchase_details')
    quantity = models.PositiveIntegerField()
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase Detail {self.product.name} - {self.quantity} - {self.amount}"

class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='payments')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE, related_name='payments')
    purchase_header = models.ForeignKey(PurchaseHeader, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    narration = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount_paid} - {self.payment_date}"

@receiver(post_save, sender=PurchaseDetail)
def increase_product_stock_on_purchase(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock += instance.quantity
        product.save()

@receiver(post_delete, sender=PurchaseDetail)
def decrease_product_stock_on_purchase_delete(sender, instance, **kwargs):
    product = instance.product
    product.stock -= instance.quantity
    product.save()
