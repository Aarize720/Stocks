from datetime import datetime
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import (
    Supplier, Product, Location, InventoryItem,
    PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem,
)
from .serializers import (
    SupplierSerializer, ProductSerializer, LocationSerializer, InventoryItemSerializer,
    PurchaseOrderSerializer, PurchaseOrderItemSerializer,
    SalesOrderSerializer, SalesOrderItemSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('name')
    serializer_class = SupplierSerializer
    filterset_fields = ['name']
    search_fields = ['name', 'email']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('sku')
    serializer_class = ProductSerializer
    filterset_fields = ['supplier', 'is_active']
    search_fields = ['sku', 'name']
    ordering_fields = ['sku', 'name', 'unit_cost', 'unit_price']


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('code')
    serializer_class = LocationSerializer


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related('product', 'location').all()
    serializer_class = InventoryItemSerializer
    filterset_fields = ['product', 'location']
    search_fields = ['product__sku', 'product__name', 'location__code']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-created_at')
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['supplier', 'status']
    search_fields = ['reference', 'supplier__name']

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        po = self.get_object()
        po.receive()
        return Response(self.get_serializer(po).data)


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all().order_by('-created_at')
    serializer_class = SalesOrderSerializer
    filterset_fields = ['status']
    search_fields = ['reference', 'customer_name']

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        so = self.get_object()
        so.complete()
        return Response(self.get_serializer(so).data)


class SalesReportView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, location='query'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, location='query'),
            OpenApiParameter(name='product', type=OpenApiTypes.INT, location='query'),
            OpenApiParameter(name='supplier', type=OpenApiTypes.INT, location='query'),
            OpenApiParameter(name='group_by', type=OpenApiTypes.STR, location='query', description='product|supplier|day|month'),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        # Filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        product_id = request.query_params.get('product')
        supplier_id = request.query_params.get('supplier')
        group_by = request.query_params.get('group_by')  # product|supplier|day|month

        items = SalesOrderItem.objects.select_related('sales_order', 'product').filter(
            sales_order__status=SalesOrder.Status.COMPLETED
        )
        if start_date:
            items = items.filter(sales_order__created_at__date__gte=start_date)
        if end_date:
            items = items.filter(sales_order__created_at__date__lte=end_date)
        if product_id:
            items = items.filter(product_id=product_id)
        if supplier_id:
            items = items.filter(product__supplier_id=supplier_id)

        revenue_expr = ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField(max_digits=18, decimal_places=2))
        cost_expr = ExpressionWrapper(F('quantity') * F('product__unit_cost'), output_field=DecimalField(max_digits=18, decimal_places=2))

        annotations = {
            'revenue': Sum(revenue_expr),
            'cost': Sum(cost_expr),
        }

        if group_by == 'product':
            qs = items.values('product_id', 'product__sku', 'product__name').annotate(**annotations)
        elif group_by == 'supplier':
            qs = items.values('product__supplier_id', 'product__supplier__name').annotate(**annotations)
        elif group_by == 'day':
            qs = items.values('sales_order__created_at__date').annotate(**annotations)
        elif group_by == 'month':
            qs = items.values('sales_order__created_at__year', 'sales_order__created_at__month').annotate(**annotations)
        else:
            qs = items.aggregate(**annotations)
            total_revenue = qs['revenue'] or 0
            total_cost = qs['cost'] or 0
            return Response({
                'revenue': total_revenue,
                'cost': total_cost,
                'profit': total_revenue - total_cost,
            })

        # For grouped results compute profit row-wise
        results = []
        for row in qs:
            revenue = row.get('revenue') or 0
            cost = row.get('cost') or 0
            row['profit'] = revenue - cost
            results.append(row)
        return Response(results)
