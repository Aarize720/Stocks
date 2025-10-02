from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    is_active = models.BooleanField(default=True)
    track_inventory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Location(models.Model):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_items')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='inventory_items')
    quantity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'location')

    def __str__(self):
        return f"{self.product.sku} @ {self.location.code}: {self.quantity}"


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending'
        RECEIVED = 'received', 'Received'
        CANCELLED = 'cancelled', 'Cancelled'

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    reference = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    expected_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    receive_location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='received_purchase_orders', null=True, blank=True)

    def __str__(self):
        return f"PO-{self.id or 'new'} {self.supplier.name} ({self.status})"

    def receive(self):
        if self.status in {self.Status.CANCELLED, self.Status.RECEIVED}:
            raise ValidationError('Cannot receive a cancelled or already received purchase order.')
        if not self.receive_location:
            raise ValidationError('receive_location must be set to receive stock.')
        for item in self.items.all():
            adjust_stock(item.product, self.receive_location, item.quantity)
        self.status = self.Status.RECEIVED
        self.save(update_fields=['status', 'updated_at'])


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_order_items')
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"POI {self.product.sku} x{self.quantity}"


class SalesOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    reference = models.CharField(max_length=64, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    ship_from = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='sales_orders', null=True, blank=True)

    def __str__(self):
        return f"SO-{self.id or 'new'} ({self.status})"

    def complete(self):
        if self.status in {self.Status.CANCELLED, self.Status.COMPLETED}:
            raise ValidationError('Cannot complete a cancelled or already completed sales order.')
        if not self.ship_from:
            raise ValidationError('ship_from must be set to complete order.')
        # Ensure stock availability
        for item in self.items.all():
            inv = InventoryItem.objects.filter(product=item.product, location=self.ship_from).first()
            available = inv.quantity if inv else 0
            if item.quantity > available:
                raise ValidationError(f'Insufficient stock for {item.product.sku} at {self.ship_from.code}.')
        # Deduct stock
        for item in self.items.all():
            adjust_stock(item.product, self.ship_from, -item.quantity)
        self.status = self.Status.COMPLETED
        self.save(update_fields=['status', 'updated_at'])


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sales_order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"SOI {self.product.sku} x{self.quantity}"


def adjust_stock(product: Product, location: Location, delta: int) -> InventoryItem:
    """Adjust stock quantity for a product at a location by delta (can be negative)."""
    inv, _ = InventoryItem.objects.get_or_create(product=product, location=location, defaults={'quantity': 0})
    inv.quantity = models.F('quantity') + delta
    inv.save(update_fields=['quantity'])
    # Refresh from DB to collapse F expression
    return InventoryItem.objects.get(pk=inv.pk)
