# Stock Control System Documentation

## Overview

The AsiriaPOS stock control system provides comprehensive inventory management capabilities with real-time tracking, automated alerts, and detailed audit trails. This system ensures accurate stock levels, prevents overselling, and provides valuable insights into inventory performance.

## Features

### 1. Real-Time Stock Tracking
- **Automatic Updates**: Stock levels are automatically updated when products are purchased or sold
- **Stock Validation**: Prevents overselling by validating stock availability before sales
- **Stock Properties**: Built-in properties to check low stock and out-of-stock status

### 2. Stock Movement Tracking
- **Complete Audit Trail**: Every stock change is recorded with reason and reference
- **Movement Types**: Purchase, Sale, Adjustment, Return, Damage/Loss, Transfer, Initial Stock
- **Historical Data**: Track stock movements over time with detailed reporting

### 3. Stock Adjustments
- **Manual Corrections**: Allow manual stock adjustments with approval workflow
- **Adjustment Types**: Stock Correction, Damage/Loss, Expiry, Theft, Physical Count, Other
- **Approval System**: Adjustments require approval before affecting stock levels

### 4. Stock Alerts
- **Automated Notifications**: Automatic alerts for low stock and out-of-stock products
- **Alert Types**: Low Stock, Out of Stock, Overstock
- **Resolution Tracking**: Track when alerts are resolved and by whom

### 5. Comprehensive Reporting
- **Stock Summary**: Total stock value, low stock counts, out-of-stock products
- **Movement Reports**: Detailed analysis of stock movements by type and time period
- **Alert Reports**: Summary of active and resolved alerts
- **Adjustment Reports**: Tracking of approved and pending adjustments

## Models

### Product Model Enhancements
```python
class Product(models.Model):
    # Existing fields...
    
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
```

### StockMovement Model
```python
class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('RETURN', 'Return'),
        ('DAMAGE', 'Damage/Loss'),
        ('TRANSFER', 'Transfer'),
        ('INITIAL', 'Initial Stock'),
    ]
    
    movement_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Positive for additions, negative for reductions
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### StockAdjustment Model
```python
class StockAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('CORRECTION', 'Stock Correction'),
        ('DAMAGE', 'Damage/Loss'),
        ('EXPIRY', 'Expiry'),
        ('THEFT', 'Theft'),
        ('PHYSICAL_COUNT', 'Physical Count'),
        ('OTHER', 'Other'),
    ]
    
    adjustment_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity_adjusted = models.IntegerField()
    reason = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
```

### StockAlert Model
```python
class StockAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('OVERSTOCK', 'Overstock'),
    ]
    
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(UserClient, on_delete=models.CASCADE, null=True, blank=True)
```

## API Endpoints

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Get product details
- `POST /api/products/` - Create new product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `GET /api/products/low_stock/` - Get products with low stock
- `GET /api/products/out_of_stock/` - Get out-of-stock products
- `GET /api/products/stock_summary/` - Get stock summary with movement history
- `GET /api/products/{id}/stock_history/` - Get stock movement history for product

### Stock Movements
- `GET /api/stock-movements/` - List all stock movements
- `GET /api/stock-movements/{id}/` - Get movement details
- `GET /api/stock-movements/summary/` - Get movement summary with filtering

### Stock Adjustments
- `GET /api/stock-adjustments/` - List all adjustments
- `POST /api/stock-adjustments/` - Create new adjustment
- `GET /api/stock-adjustments/{id}/` - Get adjustment details
- `PUT /api/stock-adjustments/{id}/` - Update adjustment
- `POST /api/stock-adjustments/{id}/approve/` - Approve adjustment
- `GET /api/stock-adjustments/pending/` - Get pending adjustments

### Stock Alerts
- `GET /api/stock-alerts/` - List all alerts
- `POST /api/stock-alerts/` - Create new alert
- `GET /api/stock-alerts/{id}/` - Get alert details
- `PUT /api/stock-alerts/{id}/` - Update alert
- `POST /api/stock-alerts/{id}/resolve/` - Resolve alert
- `GET /api/stock-alerts/active/` - Get active alerts
- `GET /api/stock-alerts/summary/` - Get alert summary

## Management Commands

### Check Stock Alerts
```bash
# Check for stock alerts
python manage.py check_stock_alerts

# Check for specific user client
python manage.py check_stock_alerts --user-client <user_client_id>

# Create new alerts for low stock products
python manage.py check_stock_alerts --create-alerts
```

### Generate Stock Reports
```bash
# Generate summary report
python manage.py stock_report --report-type summary

# Generate movements report for last 30 days
python manage.py stock_report --report-type movements --days 30

# Generate all reports
python manage.py stock_report --report-type all --days 60

# Generate report for specific user client
python manage.py stock_report --user-client <user_client_id> --report-type all
```

## Usage Examples

### Creating a Stock Adjustment
```python
from products.models import StockAdjustment

# Create a stock adjustment
adjustment = StockAdjustment.objects.create(
    user_client=user_client,
    product=product,
    adjustment_type='PHYSICAL_COUNT',
    quantity_adjusted=5,  # Add 5 units
    reason='Physical count correction',
    reference_number='PC-001',
    created_by=user
)

# Approve the adjustment
adjustment.approve(approved_by_user)
```

### Checking Stock Status
```python
from products.models import Product

# Check if product is low on stock
if product.is_low_stock:
    print(f"{product.name} is running low on stock")

# Check if product is out of stock
if product.is_out_of_stock:
    print(f"{product.name} is out of stock")

# Get stock value
stock_value = product.stock_value
print(f"Stock value: ${stock_value:,.2f}")
```

### Getting Stock Movement History
```python
# Get recent movements for a product
movements = product.stock_movements.order_by('-created_at')[:10]

for movement in movements:
    print(f"{movement.movement_type}: {movement.quantity} units")
    print(f"Stock changed from {movement.previous_stock} to {movement.new_stock}")
    print(f"Reason: {movement.reason}")
```

## Database Migrations

After implementing the stock control system, run the following commands:

```bash
# Create migrations
python manage.py makemigrations products

# Apply migrations
python manage.py migrate
```

## Configuration

### Settings
The stock control system uses Django's standard settings. No additional configuration is required.

### Permissions
The system respects Django's permission system. Users need appropriate permissions to:
- View products and stock information
- Create and approve stock adjustments
- Resolve stock alerts
- Access stock reports

## Best Practices

1. **Regular Stock Checks**: Use the management commands to regularly check for stock alerts
2. **Approval Workflow**: Always require approval for stock adjustments to maintain data integrity
3. **Documentation**: Provide clear reasons for all stock adjustments
4. **Monitoring**: Regularly review stock movement reports to identify patterns
5. **Backup**: Ensure regular backups of stock data

## Troubleshooting

### Common Issues

1. **Stock not updating**: Check if the signals are properly connected
2. **Alerts not generating**: Verify that the alert conditions are met
3. **Adjustments not approved**: Ensure the approval workflow is followed correctly

### Debug Commands
```bash
# Check stock levels
python manage.py shell
>>> from products.models import Product
>>> Product.objects.filter(stock__lte=0).count()

# Check active alerts
>>> from products.models import StockAlert
>>> StockAlert.objects.filter(is_active=True).count()
```

## Future Enhancements

1. **Email Notifications**: Send email alerts for stock issues
2. **Barcode Integration**: Enhanced barcode scanning for stock operations
3. **Mobile App**: Mobile interface for stock management
4. **Advanced Analytics**: Predictive stock analysis and forecasting
5. **Multi-location Support**: Stock management across multiple locations
6. **Integration**: Integration with external inventory systems
