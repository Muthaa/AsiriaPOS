from django.core.management.base import BaseCommand
from django.db.models import Q, F
from products.models import Product, StockAlert
from users.models import UserClient


class Command(BaseCommand):
    help = 'Check for stock alerts and generate notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-client',
            type=str,
            help='User client ID to check alerts for (optional)',
        )
        parser.add_argument(
            '--create-alerts',
            action='store_true',
            help='Create new alerts for products with low stock',
        )

    def handle(self, *args, **options):
        user_client_id = options.get('user_client')
        create_alerts = options.get('create_alerts')

        # Filter products by user client if specified
        products_queryset = Product.objects.all()
        if user_client_id:
            try:
                user_client = UserClient.objects.get(user_client_id=user_client_id)
                products_queryset = products_queryset.filter(user_client=user_client)
                self.stdout.write(f"Checking stock alerts for user client: {user_client.username}")
            except UserClient.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User client with ID {user_client_id} not found"))
                return

        # Check for low stock products
        low_stock_products = products_queryset.filter(stock__lte=F('minQuantity'))
        out_of_stock_products = products_queryset.filter(stock__lte=0)

        self.stdout.write(f"Found {low_stock_products.count()} products with low stock")
        self.stdout.write(f"Found {out_of_stock_products.count()} products out of stock")

        if create_alerts:
            alerts_created = 0
            
            # Create low stock alerts
            for product in low_stock_products:
                alert, created = StockAlert.objects.get_or_create(
                    user_client=product.user_client,
                    product=product,
                    alert_type='LOW_STOCK',
                    is_active=True,
                    defaults={
                        'message': f"Product {product.name} is running low on stock. Current stock: {product.stock}, Minimum: {product.minQuantity}"
                    }
                )
                if created:
                    alerts_created += 1
                    self.stdout.write(f"Created low stock alert for {product.name}")

            # Create out of stock alerts
            for product in out_of_stock_products:
                alert, created = StockAlert.objects.get_or_create(
                    user_client=product.user_client,
                    product=product,
                    alert_type='OUT_OF_STOCK',
                    is_active=True,
                    defaults={
                        'message': f"Product {product.name} is out of stock!"
                    }
                )
                if created:
                    alerts_created += 1
                    self.stdout.write(f"Created out of stock alert for {product.name}")

            self.stdout.write(self.style.SUCCESS(f"Created {alerts_created} new stock alerts"))

        # Display summary
        active_alerts = StockAlert.objects.filter(is_active=True)
        if user_client_id:
            active_alerts = active_alerts.filter(user_client__user_client_id=user_client_id)

        self.stdout.write(f"Total active alerts: {active_alerts.count()}")

        # Show low stock products
        if low_stock_products.exists():
            self.stdout.write("\nLow Stock Products:")
            for product in low_stock_products:
                self.stdout.write(f"  - {product.name}: {product.stock}/{product.minQuantity}")

        # Show out of stock products
        if out_of_stock_products.exists():
            self.stdout.write("\nOut of Stock Products:")
            for product in out_of_stock_products:
                self.stdout.write(f"  - {product.name}: {product.stock}")
