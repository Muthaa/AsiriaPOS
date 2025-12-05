import uuid
from django.db import models
from users.models import UserClient
from products.models import Product, Unit, Category, StockMovement, StockAlert
from registry.models import Customer, PaymentOption
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from Domain.models import AuditLog 

class SalesHeader(models.Model):
    sales_header_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=255, unique=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    # Anonymous and link keys
    anonymous_customer_id = models.UUIDField(blank=True, null=True)
    mpesa_token_hash = models.CharField(max_length=128, blank=True, null=True)
    card_token_hash = models.CharField(max_length=128, blank=True, null=True)
    credit_account_code = models.CharField(max_length=64, blank=True, null=True)
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE', 'Mobile Money'),
        ('CREDIT', 'Store Credit'),
        ('OTHER', 'Other'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH')
    terminal_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Sale Header {self.order_number} by {self.user_client.username}"

class SalesDetail(models.Model):
    sales_detail_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
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

    def clean(self):
        """Validate stock availability before saving"""
        if self.product and self.quantity:
            if self.product.stock < self.quantity:
                raise ValidationError(f"Insufficient stock. Available: {self.product.stock}, Requested: {self.quantity}")
    
    def save(self, *args, **kwargs):
        is_create = self._state.adding
        before_price = None
        if not is_create:
            try:
                before_price = SalesDetail.objects.get(pk=self.pk).price_per_unit
            except SalesDetail.DoesNotExist:
                pass
        self.clean()
        super().save(*args, **kwargs)
        # Audit price override
        if before_price is not None and before_price != self.price_per_unit:
            AuditLog.objects.create(
                user=None,
                action='PRICE_OVERRIDE',
                model_name='SalesDetail',
                object_id=str(self.pk),
                reason='Price changed on sales detail',
                before_data={'price_per_unit': float(before_price)},
                after_data={'price_per_unit': float(self.price_per_unit)}
            )
    
class Receipt(models.Model):
    receipt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    payment_option = models.ForeignKey(PaymentOption, on_delete=models.CASCADE)
    sales_header = models.ForeignKey(SalesHeader, on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=255, unique=True)
    # Short token printed/encoded in QR to link later
    link_token = models.CharField(max_length=16, blank=True, null=True, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    # Anonymous and link keys mirrored on receipt for quick queries
    anonymous_customer_id = models.UUIDField(blank=True, null=True)
    mpesa_token_hash = models.CharField(max_length=128, blank=True, null=True)
    card_token_hash = models.CharField(max_length=128, blank=True, null=True)
    credit_account_code = models.CharField(max_length=64, blank=True, null=True)
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE', 'Mobile Money'),
        ('CREDIT', 'Store Credit'),
        ('OTHER', 'Other'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH')
    payment_date = models.DateTimeField(auto_now_add=True)
    narration = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Receipt {self.receipt_number} for Sale {self.sales_header.order_number}"

class SalesReservation(models.Model):
    reservation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    sales_header = models.ForeignKey(SalesHeader, on_delete=models.CASCADE, related_name='reservations')
    sales_detail = models.ForeignKey(SalesDetail, on_delete=models.CASCADE, related_name='reservation', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reservations')
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    expiry_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reserve {self.product.name} x{self.quantity} ({'ACTIVE' if self.is_active else 'RELEASED'})"

class SalesReturn(models.Model):
    RETURN_REASONS = [
        ('DAMAGED', 'Damaged'),
        ('EXCESS', 'Excess'),
        ('WRONG_ITEM', 'Wrong Item'),
        ('OTHER', 'Other'),
    ]
    sales_return_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    sales_header = models.ForeignKey(SalesHeader, on_delete=models.CASCADE, related_name='returns')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=20, choices=RETURN_REASONS, default='OTHER')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(UserClient, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_returns_approved')
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Return {self.sales_return_id} for {self.product.name}"

    def approve(self, approver):
        if self.is_approved:
            raise ValidationError('Return already approved')
        self.is_approved = True
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()
        AuditLog.objects.create(
            user=None,
            action='REFUND',
            model_name='SalesReturn',
            object_id=str(self.sales_return_id),
            reason='Return approved',
            before_data=None,
            after_data={'approved': True, 'quantity': self.quantity}
        )

class SalesRefund(models.Model):
    REFUND_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE', 'Mobile Money'),
        ('STORE_CREDIT', 'Store Credit'),
    ]
    refund_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    sales_header = models.ForeignKey(SalesHeader, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=REFUND_METHODS)
    reference = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(UserClient, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_refunds_approved')
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount}"

    def approve(self, approver):
        if self.is_approved:
            raise ValidationError('Refund already approved')
        self.is_approved = True
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()
        AuditLog.objects.create(
            user=None,
            action='REFUND',
            model_name='SalesRefund',
            object_id=str(self.refund_id),
            reason='Refund approved',
            before_data=None,
            after_data={'approved': True, 'amount': float(self.amount)}
        )

class CashSession(models.Model):
    SESSION_STATUS = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    opened_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='cash_sessions_opened')
    closed_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='cash_sessions_closed', null=True, blank=True)
    opening_float = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=SESSION_STATUS, default='OPEN')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.session_id} - {self.status}"

    def close(self, closed_by_user, closing_total_amount):
        if self.status == 'CLOSED':
            raise ValidationError('Session already closed')
        self.status = 'CLOSED'
        self.closed_by = closed_by_user
        self.closed_at = timezone.now()
        self.closing_total = closing_total_amount
        self.save()

class SalesPayment(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE', 'Mobile Money'),
        ('BANK', 'Bank Transfer'),
        ('OTHER', 'Other'),
    ]

    sales_payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    sales_header = models.ForeignKey(SalesHeader, on_delete=models.CASCADE, related_name='payments')
    session = models.ForeignKey(CashSession, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.sales_payment_id} - {self.method} - {self.amount}"

@receiver(post_save, sender=SalesDetail)
def decrease_product_stock_on_sale(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        previous_stock = product.stock
        product.stock -= instance.quantity
        product.save()
        
        # Create stock movement record
        StockMovement.objects.create(
            user_client=instance.user_client,
            product=product,
            movement_type='SALE',
            quantity=-instance.quantity,
            previous_stock=previous_stock,
            new_stock=product.stock,
            reference_number=instance.sales_header.order_number,
            reason=f"Sale to {instance.sales_header.customer.name}",
            created_by=instance.user_client
        )
        
        # Check for low stock alerts
        if product.is_low_stock:
            StockAlert.objects.get_or_create(
                user_client=instance.user_client,
                product=product,
                alert_type='LOW_STOCK',
                defaults={
                    'message': f"Product {product.name} is running low on stock. Current stock: {product.stock}, Minimum: {product.minQuantity}",
                    'is_active': True
                }
            )
        
        # Check for out of stock alerts
        if product.is_out_of_stock:
            StockAlert.objects.get_or_create(
                user_client=instance.user_client,
                product=product,
                alert_type='OUT_OF_STOCK',
                defaults={
                    'message': f"Product {product.name} is out of stock!",
                    'is_active': True
                }
            )

@receiver(post_delete, sender=SalesDetail)
def increase_product_stock_on_sale_delete(sender, instance, **kwargs):
    product = instance.product
    previous_stock = product.stock
    product.stock += instance.quantity
    product.save()
    
    # Create stock movement record for reversal
    StockMovement.objects.create(
        user_client=instance.user_client,
        product=product,
        movement_type='ADJUSTMENT',
        quantity=instance.quantity,
        previous_stock=previous_stock,
        new_stock=product.stock,
        reference_number=f"REVERSAL-{instance.sales_header.order_number}",
        reason="Sale detail deleted - stock reversal",
        created_by=instance.user_client
    )

@receiver(post_save, sender=SalesReturn)
def increase_stock_on_return(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        previous_stock = product.stock
        product.stock += instance.quantity
        product.save()
        StockMovement.objects.create(
            user_client=instance.user_client,
            product=product,
            movement_type='RETURN',
            quantity=instance.quantity,
            previous_stock=previous_stock,
            new_stock=product.stock,
            reference_number=instance.sales_header.order_number,
            reason=f"Return: {instance.get_reason_display()}",
            created_by=instance.user_client
        )
        AuditLog.objects.create(
            user=None,
            action='REFUND',
            model_name='SalesReturn',
            object_id=str(instance.sales_return_id),
            reason=instance.notes or instance.get_reason_display(),
            before_data=None,
            after_data={'product': str(instance.product_id), 'quantity': instance.quantity}
        )