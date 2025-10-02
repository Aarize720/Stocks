from django.contrib import admin
from .models import (
    Supplier, Product, Location, InventoryItem,
    PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "supplier", "unit_cost", "unit_price", "is_active")
    list_filter = ("is_active", "supplier")
    search_fields = ("sku", "name")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("product", "location", "quantity", "reorder_threshold")
    list_filter = ("location",)
    search_fields = ("product__sku", "product__name", "location__code")


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "status", "expected_date", "created_at")
    list_filter = ("status", "supplier")
    inlines = [PurchaseOrderItemInline]


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 0


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "reference", "customer_name", "status", "created_at")
    list_filter = ("status",)
    inlines = [SalesOrderItemInline]
