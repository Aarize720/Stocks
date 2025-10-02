from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models
from inventory.models import InventoryItem

class Command(BaseCommand):
    help = "List low stock items (quantity <= reorder_threshold) and optionally send alerts"

    def add_arguments(self, parser):
        parser.add_argument('--email', action='store_true', help='Send alert emails (requires EMAIL settings)')

    def handle(self, *args, **options):
        low = InventoryItem.objects.select_related('product', 'location').filter(quantity__lte=models.F('reorder_threshold'))
        if not low.exists():
            self.stdout.write(self.style.SUCCESS('No low stock items.'))
            return

        lines = []
        for item in low:
            lines.append(f"{item.product.sku} - {item.product.name} @ {item.location.code}: qty={item.quantity}, threshold={item.reorder_threshold}")
        report = "\n".join(lines)
        self.stdout.write(report)

        if options['email']:
            # Placeholder: requires EMAIL_* settings to be configured
            try:
                from django.core.mail import send_mail
                subject = 'Low stock alert'
                body = report
                recipient = getattr(settings, 'STOCK_ALERT_EMAIL', None)
                if not recipient:
                    self.stdout.write(self.style.WARNING('STOCK_ALERT_EMAIL not set; skipping email'))
                    return
                send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient])
                self.stdout.write(self.style.SUCCESS('Alert email sent'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))
