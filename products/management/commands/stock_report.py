from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from products.models import Product, StockMovement, StockAdjustment, StockAlert
from users.models import UserClient


class Command(BaseCommand):
    help = 'Generate comprehensive stock reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-client',
            type=str,
            help='User client ID to generate report for (optional)',
        )
        parser.add_argument(
            '--report-type',
            type=str,
            choices=['summary', 'movements', 'alerts', 'adjustments', 'all'],
            default='summary',
            help='Type of report to generate',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to include in the report (default: 30)',
        )

    def handle(self, *args, **options):
        user_client_id = options.get('user_client')
        report_type = options.get('report_type')
        days = options.get('days')

        # Filter by user client if specified
        user_client = None
        if user_client_id:
            try:
                user_client = UserClient.objects.get(user_client_id=user_client_id)
                self.stdout.write(f"Generating report for user client: {user_client.username}")
            except UserClient.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User client with ID {user_client_id} not found"))
                return

        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        if report_type in ['summary', 'all']:
            self.generate_summary_report(user_client, start_date, end_date)

        if report_type in ['movements', 'all']:
            self.generate_movements_report(user_client, start_date, end_date)

        if report_type in ['alerts', 'all']:
            self.generate_alerts_report(user_client, start_date, end_date)

        if report_type in ['adjustments', 'all']:
            self.generate_adjustments_report(user_client, start_date, end_date)

    def generate_summary_report(self, user_client, start_date, end_date):
        """Generate stock summary report"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("STOCK SUMMARY REPORT")
        self.stdout.write("="*50)

        # Filter products
        products_queryset = Product.objects.all()
        if user_client:
            products_queryset = products_queryset.filter(user_client=user_client)

        # Calculate totals
        total_products = products_queryset.count()
        # Calculate total stock value manually since it's a property
        total_stock_value = sum(product.stock_value for product in products_queryset)
        low_stock_count = products_queryset.filter(stock__lte=F('minQuantity')).count()
        out_of_stock_count = products_queryset.filter(stock__lte=0).count()

        self.stdout.write(f"Total Products: {total_products}")
        self.stdout.write(f"Total Stock Value: ${total_stock_value:,.2f}")
        self.stdout.write(f"Low Stock Products: {low_stock_count}")
        self.stdout.write(f"Out of Stock Products: {out_of_stock_count}")

        # Top products by stock value
        top_products = sorted(products_queryset, key=lambda p: p.stock_value, reverse=True)[:10]
        if top_products:
            self.stdout.write("\nTop 10 Products by Stock Value:")
            for product in top_products:
                self.stdout.write(f"  - {product.name}: {product.stock} units @ ${product.cost} = ${product.stock_value:,.2f}")

    def generate_movements_report(self, user_client, start_date, end_date):
        """Generate stock movements report"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("STOCK MOVEMENTS REPORT")
        self.stdout.write("="*50)

        # Filter movements
        movements_queryset = StockMovement.objects.filter(
            created_at__range=(start_date, end_date)
        )
        if user_client:
            movements_queryset = movements_queryset.filter(user_client=user_client)

        # Summary
        total_movements = movements_queryset.count()
        total_in = movements_queryset.filter(quantity__gt=0).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        total_out = abs(movements_queryset.filter(quantity__lt=0).aggregate(
            total=Sum('quantity')
        )['total'] or 0)

        self.stdout.write(f"Period: {start_date.date()} to {end_date.date()}")
        self.stdout.write(f"Total Movements: {total_movements}")
        self.stdout.write(f"Total Stock In: {total_in}")
        self.stdout.write(f"Total Stock Out: {total_out}")

        # Movements by type
        movements_by_type = movements_queryset.values('movement_type').annotate(
            count=Count('movement_id'),
            total_quantity=Sum('quantity')
        )

        if movements_by_type:
            self.stdout.write("\nMovements by Type:")
            for movement_type in movements_by_type:
                self.stdout.write(f"  - {movement_type['movement_type']}: {movement_type['count']} movements, {movement_type['total_quantity']} units")

    def generate_alerts_report(self, user_client, start_date, end_date):
        """Generate stock alerts report"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("STOCK ALERTS REPORT")
        self.stdout.write("="*50)

        # Filter alerts
        alerts_queryset = StockAlert.objects.filter(
            created_at__range=(start_date, end_date)
        )
        if user_client:
            alerts_queryset = alerts_queryset.filter(user_client=user_client)

        # Summary
        total_alerts = alerts_queryset.count()
        active_alerts = alerts_queryset.filter(is_active=True).count()
        resolved_alerts = alerts_queryset.filter(is_active=False).count()

        self.stdout.write(f"Period: {start_date.date()} to {end_date.date()}")
        self.stdout.write(f"Total Alerts: {total_alerts}")
        self.stdout.write(f"Active Alerts: {active_alerts}")
        self.stdout.write(f"Resolved Alerts: {resolved_alerts}")

        # Alerts by type
        alerts_by_type = alerts_queryset.values('alert_type').annotate(
            count=Count('alert_id'),
            active_count=Count('alert_id', filter=Q(is_active=True))
        )

        if alerts_by_type:
            self.stdout.write("\nAlerts by Type:")
            for alert_type in alerts_by_type:
                self.stdout.write(f"  - {alert_type['alert_type']}: {alert_type['count']} total, {alert_type['active_count']} active")

    def generate_adjustments_report(self, user_client, start_date, end_date):
        """Generate stock adjustments report"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("STOCK ADJUSTMENTS REPORT")
        self.stdout.write("="*50)

        # Filter adjustments
        adjustments_queryset = StockAdjustment.objects.filter(
            created_at__range=(start_date, end_date)
        )
        if user_client:
            adjustments_queryset = adjustments_queryset.filter(user_client=user_client)

        # Summary
        total_adjustments = adjustments_queryset.count()
        approved_adjustments = adjustments_queryset.filter(is_approved=True).count()
        pending_adjustments = adjustments_queryset.filter(is_approved=False).count()
        total_adjusted = adjustments_queryset.aggregate(
            total=Sum('quantity_adjusted')
        )['total'] or 0

        self.stdout.write(f"Period: {start_date.date()} to {end_date.date()}")
        self.stdout.write(f"Total Adjustments: {total_adjustments}")
        self.stdout.write(f"Approved: {approved_adjustments}")
        self.stdout.write(f"Pending: {pending_adjustments}")
        self.stdout.write(f"Total Quantity Adjusted: {total_adjusted}")

        # Adjustments by type
        adjustments_by_type = adjustments_queryset.values('adjustment_type').annotate(
            count=Count('adjustment_id'),
            total_quantity=Sum('quantity_adjusted')
        )

        if adjustments_by_type:
            self.stdout.write("\nAdjustments by Type:")
            for adjustment_type in adjustments_by_type:
                self.stdout.write(f"  - {adjustment_type['adjustment_type']}: {adjustment_type['count']} adjustments, {adjustment_type['total_quantity']} units")
