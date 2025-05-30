from django.db import models
from users.models import UserClient  # Import UserClient if it exists in users.models

# Create your models here.
# This is the Product model for the AsiriaPOS application.

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Unit(models.Model):
    unit_id = models.AutoField(primary_key=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='units')
    unit_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.unit_name

import uuid   
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255, unique=True)
    barcode = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    sku = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    minQuantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
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



