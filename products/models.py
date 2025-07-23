import uuid
from django.db import models
from users.models import UserClient 

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
    description = models.TextField(blank=True)
    minQuantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
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



