from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Product

class Command(BaseCommand):
    help = "Make flash_start and flash_end timezone-aware for all flash sale products"

    def handle(self, *args, **options):
        count = 0
        for product in Product.objects.filter(is_flash_sale=True):
            updated = False
            if product.flash_start and timezone.is_naive(product.flash_start):
                product.flash_start = timezone.make_aware(product.flash_start)
                updated = True
            if product.flash_end and timezone.is_naive(product.flash_end):
                product.flash_end = timezone.make_aware(product.flash_end)
                updated = True
            if updated:
                product.save()
                count += 1
                self.stdout.write(f"Updated {product.title}")
        self.stdout.write(self.style.SUCCESS(f"Finished! Updated {count} products."))
