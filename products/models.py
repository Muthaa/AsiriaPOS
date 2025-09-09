import uuid
from django.db import models
from users.models import UserClient 
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
# This is the Product model for the AsiriaPOS application.

class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Unit(models.Model):
    unit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='units')
    unit_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.unit_name

class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=20, unique=True, blank=True)
    barcode = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    minQuantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    # is_active = models.BooleanField(default=True)
    # is_featured = models.BooleanField(default=False)
    # is_on_sale = models.BooleanField(default=False)
    # is_new = models.BooleanField(default=False)
    # is_best_seller = models.BooleanField(default=False)
    # is_trending = models.BooleanField(default=False)
    # is_discounted = models.BooleanField(default=False)
    # is_out_of_stock = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        """Check if product is running low on stock"""
        return self.stock <= self.minQuantity

    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.stock <= 0

    @property
    def stock_value(self):
        """Calculate total stock value"""
        return self.stock * self.cost

    def save(self, *args, **kwargs):
        if not self.sku or self.sku == '':
            if self.category and self.category.name:
                # cat_initials = ''.join([word[0] for word in self.category.name.split()][:3]).upper()
                cat_initials = self.category.name[:3].upper()
            else:
                cat_initials = 'GEN'
            count = Product.objects.filter(category=self.category).count() + 1
            self.sku = f"{cat_initials}-{count:05d}"
        if not self.barcode or self.barcode == '':
            self.barcode = self.generate_unique_barcode()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_barcode():
        import uuid
        while True:
            barcode = str(uuid.uuid4().int)[:13]
            if not Product.objects.filter(barcode=barcode).exists():
                return barcode

class StockMovement(models.Model):
    """Track all stock movements with reasons"""
    MOVEMENT_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('RETURN', 'Return'),
        ('DAMAGE', 'Damage/Loss'),
        ('TRANSFER', 'Transfer'),
        ('INITIAL', 'Initial Stock'),
    ]

    movement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Positive for additions, negative for reductions
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_number = models.CharField(max_length=100, blank=True, null=True)  # Invoice, order number, etc.
    reason = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='stock_movements_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.previous_stock:
            self.previous_stock = self.product.stock
        if not self.new_stock:
            self.new_stock = self.previous_stock + self.quantity
        super().save(*args, **kwargs)

class StockAdjustment(models.Model):
    """Manual stock adjustments"""
    ADJUSTMENT_TYPES = [
        ('CORRECTION', 'Stock Correction'),
        ('DAMAGE', 'Damage/Loss'),
        ('EXPIRY', 'Expiry'),
        ('THEFT', 'Theft'),
        ('PHYSICAL_COUNT', 'Physical Count'),
        ('OTHER', 'Other'),
    ]

    adjustment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity_adjusted = models.IntegerField()  # Can be positive or negative
    reason = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='stock_adjustments_created')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='stock_adjustments_approved', null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.adjustment_type} - {self.product.name} - {self.quantity_adjusted}"

    def approve(self, approved_by_user):
        """Approve the stock adjustment"""
        if not self.is_approved:
            self.is_approved = True
            self.approved_by = approved_by_user
            self.approved_at = timezone.now()
            
            # Update product stock
            self.product.stock += self.quantity_adjusted
            
            # Create stock movement record
            StockMovement.objects.create(
                user_client=self.user_client,
                product=self.product,
                movement_type='ADJUSTMENT',
                quantity=self.quantity_adjusted,
                previous_stock=self.product.stock - self.quantity_adjusted,
                new_stock=self.product.stock,
                reference_number=self.reference_number,
                reason=self.reason,
                created_by=self.created_by
            )
            
            self.product.save()
            self.save()

class StockAlert(models.Model):
    """Stock alerts for low stock notifications"""
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('OVERSTOCK', 'Overstock'),
    ]

    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='stock_alerts_resolved', null=True, blank=True)

    def __str__(self):
        return f"{self.alert_type} - {self.product.name}"

    def resolve(self, resolved_by_user):
        """Resolve the stock alert"""
        self.is_active = False
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by_user
        self.save()

class Location(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        unique_together = ('user_client', 'name')

class ProductLocationStock(models.Model):
    pls_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='product_location_stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='location_stocks')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(default=0)
    min_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'location')

    def __str__(self):
        return f"{self.product.name} @ {self.location.code}: {self.quantity}"

class StockTransfer(models.Model):
    transfer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='stock_transfers')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_transfers')
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='transfers_out')
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='transfers_in')
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='stock_transfers_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer {self.product.name} {self.quantity} {self.from_location.code}->{self.to_location.code}"

    def clean(self):
        if self.from_location_id == self.to_location_id:
            raise ValidationError('From and To locations must be different')

    def apply(self):
        self.clean()
        # Fetch or create per-location stock records
        src, _ = ProductLocationStock.objects.get_or_create(
            user_client=self.user_client, product=self.product, location=self.from_location,
            defaults={'quantity': 0}
        )
        dst, _ = ProductLocationStock.objects.get_or_create(
            user_client=self.user_client, product=self.product, location=self.to_location,
            defaults={'quantity': 0}
        )
        if src.quantity < self.quantity:
            raise ValidationError('Insufficient stock at source location')
        previous_src = src.quantity
        previous_dst = dst.quantity
        src.quantity -= self.quantity
        dst.quantity += self.quantity
        src.save()
        dst.save()
        # Log movements
        StockMovement.objects.create(
            user_client=self.user_client,
            product=self.product,
            movement_type='TRANSFER',
            quantity=-int(self.quantity),
            previous_stock=previous_src,
            new_stock=src.quantity,
            reference_number=self.reference,
            reason=f"Transfer out to {self.to_location.code}",
            created_by=self.created_by
        )
        StockMovement.objects.create(
            user_client=self.user_client,
            product=self.product,
            movement_type='TRANSFER',
            quantity=int(self.quantity),
            previous_stock=previous_dst,
            new_stock=dst.quantity,
            reference_number=self.reference,
            reason=f"Transfer in from {self.from_location.code}",
            created_by=self.created_by
        )



