from rest_framework import serializers
from .models import (
    Supplier, Product, Location, InventoryItem,
    PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem,
)


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='supplier.name')

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'unit_cost', 'unit_price',
            'supplier', 'supplier_name', 'is_active', 'track_inventory'
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class InventoryItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    location_detail = LocationSerializer(source='location', read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'product', 'product_detail', 'location', 'location_detail', 'quantity', 'reorder_threshold']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'unit_cost']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name')

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'reference', 'status',
            'expected_date', 'created_at', 'updated_at', 'receive_location', 'items'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        po = PurchaseOrder.objects.create(**validated_data)
        for item in items_data:
            PurchaseOrderItem.objects.create(purchase_order=po, **item)
        return po

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                PurchaseOrderItem.objects.create(purchase_order=instance, **item)
        return instance


class SalesOrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = SalesOrderItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'unit_price']


class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'reference', 'customer_name', 'status', 'created_at', 'updated_at', 'ship_from', 'items'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        so = SalesOrder.objects.create(**validated_data)
        for item in items_data:
            SalesOrderItem.objects.create(sales_order=so, **item)
        return so

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                SalesOrderItem.objects.create(sales_order=instance, **item)
        return instance