import uuid
from django.db import models
from products.models import Product, Unit, StockMovement
from users.models import UserClient
from registry.models import Supplier, PaymentOption
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

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

class PurchaseOrderHeader(models.Model):
    po_header_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='po_headers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='po_headers')
    order_number = models.CharField(max_length=255, unique=True)
    expected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO {self.order_number} - {self.supplier.name}"

class PurchaseOrderDetail(models.Model):
    po_detail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='po_details')
    po_header = models.ForeignKey(PurchaseOrderHeader, on_delete=models.CASCADE, related_name='po_details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='po_details')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='po_details')
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO Detail {self.product.name} - {self.quantity}"

class GRNHeader(models.Model):
    grn_header_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='grn_headers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='grn_headers')
    po_header = models.ForeignKey(PurchaseOrderHeader, on_delete=models.SET_NULL, null=True, blank=True, related_name='grn_headers')
    grn_number = models.CharField(max_length=255, unique=True)
    received_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GRN {self.grn_number} - {self.supplier.name}"

class GRNDetail(models.Model):
    grn_detail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='grn_details')
    grn_header = models.ForeignKey(GRNHeader, on_delete=models.CASCADE, related_name='grn_details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='grn_details')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='grn_details')
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GRN Detail {self.product.name} - {self.quantity}"

@receiver(post_save, sender=PurchaseDetail)
def increase_product_stock_on_purchase(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        previous_stock = product.stock
        product.stock += instance.quantity
        # Weighted average cost update
        try:
            current_qty = previous_stock
            current_cost = product.average_cost or product.cost
            incoming_qty = instance.quantity
            incoming_cost = float(instance.price_per_unit) - float(instance.discount or 0)
            new_avg = ((current_qty * float(current_cost)) + (incoming_qty * incoming_cost)) / max(current_qty + incoming_qty, 1)
            product.average_cost = new_avg
        except Exception:
            pass
        product.save()
        
        # Create stock movement record
        StockMovement.objects.create(
            user_client=instance.user_client,
            product=product,
            movement_type='PURCHASE',
            quantity=instance.quantity,
            previous_stock=previous_stock,
            new_stock=product.stock,
            reference_number=instance.purchase_header.invoice_number,
            reason=f"Purchase from {instance.purchase_header.supplier.name}",
            created_by=instance.user_client
        )

@receiver(post_delete, sender=PurchaseDetail)
def decrease_product_stock_on_purchase_delete(sender, instance, **kwargs):
    product = instance.product
    previous_stock = product.stock
    product.stock -= instance.quantity
    product.save()
    
    # Create stock movement record for reversal
    StockMovement.objects.create(
        user_client=instance.user_client,
        product=product,
        movement_type='ADJUSTMENT',
        quantity=-instance.quantity,
        previous_stock=previous_stock,
        new_stock=product.stock,
        reference_number=f"REVERSAL-{instance.purchase_header.invoice_number}",
        reason="Purchase detail deleted - stock reversal",
        created_by=instance.user_client
    )

@receiver(post_save, sender=GRNDetail)
def increase_product_stock_on_grn(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        previous_stock = product.stock
        product.stock += instance.quantity
        # Weighted average cost update on GRN
        try:
            current_qty = previous_stock
            current_cost = product.average_cost or product.cost
            incoming_qty = instance.quantity
            incoming_cost = float(instance.price_per_unit)
            new_avg = ((current_qty * float(current_cost)) + (incoming_qty * incoming_cost)) / max(current_qty + incoming_qty, 1)
            product.average_cost = new_avg
        except Exception:
            pass
        product.save()
        StockMovement.objects.create(
            user_client=instance.user_client,
            product=product,
            movement_type='PURCHASE',
            quantity=instance.quantity,
            previous_stock=previous_stock,
            new_stock=product.stock,
            reference_number=instance.grn_header.grn_number,
            reason=f"GRN from {instance.grn_header.supplier.name}",
            created_by=instance.user_client
        )

@receiver(post_delete, sender=GRNDetail)
def decrease_product_stock_on_grn_delete(sender, instance, **kwargs):
    product = instance.product
    previous_stock = product.stock
    product.stock -= instance.quantity
    product.save()
    StockMovement.objects.create(
        user_client=instance.user_client,
        product=product,
        movement_type='ADJUSTMENT',
        quantity=-instance.quantity,
        previous_stock=previous_stock,
        new_stock=product.stock,
        reference_number=f"REVERSAL-{instance.grn_header.grn_number}",
        reason="GRN detail deleted - stock reversal",
        created_by=instance.user_client
    )
