from django.core.management.base import BaseCommand
from django.utils import timezone
from sales.models import SalesReservation


class Command(BaseCommand):
    help = 'Release expired sales reservations'

    def handle(self, *args, **options):
        now = timezone.now()
        qs = SalesReservation.objects.filter(is_active=True, expiry_at__isnull=False, expiry_at__lte=now)
        count = qs.count()
        qs.update(is_active=False, released_at=now)
        self.stdout.write(self.style.SUCCESS(f'Released {count} expired reservations'))


