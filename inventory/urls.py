from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, ProductViewSet, LocationViewSet, InventoryItemViewSet,
    PurchaseOrderViewSet, SalesOrderViewSet, SalesReportView,
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'inventory', InventoryItemViewSet)
router.register(r'purchase-orders', PurchaseOrderViewSet)
router.register(r'sales-orders', SalesOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
]