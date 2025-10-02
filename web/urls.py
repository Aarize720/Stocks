from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    SignUpView, DashboardView,
    SupplierListView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    LocationListView, LocationCreateView, LocationUpdateView, LocationDeleteView,
    InventoryItemListView, InventoryItemCreateView, InventoryItemUpdateView, InventoryItemDeleteView,
    PurchaseOrderListView, PurchaseOrderCreateView, PurchaseOrderUpdateView, PurchaseOrderReceiveView,
    SalesOrderListView, SalesOrderCreateView, SalesOrderUpdateView, SalesOrderCompleteView,
)
from .views import InventoryAdjustView

app_name = "web"

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),

    # Suppliers
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier-edit'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier-delete'),

    # Products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    # Locations
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/create/', LocationCreateView.as_view(), name='location-create'),
    path('locations/<int:pk>/edit/', LocationUpdateView.as_view(), name='location-edit'),
    path('locations/<int:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),

    # Inventory
    path('inventory/', InventoryItemListView.as_view(), name='inventory-list'),
    path('inventory/create/', InventoryItemCreateView.as_view(), name='inventory-create'),
    path('inventory/<int:pk>/edit/', InventoryItemUpdateView.as_view(), name='inventory-edit'),
    path('inventory/<int:pk>/delete/', InventoryItemDeleteView.as_view(), name='inventory-delete'),
    path('inventory/<int:pk>/adjust/', InventoryAdjustView.as_view(), name='inventory-adjust'),

    # Purchase Orders
    path('purchase-orders/', PurchaseOrderListView.as_view(), name='po-list'),
    path('purchase-orders/create/', PurchaseOrderCreateView.as_view(), name='po-create'),
    path('purchase-orders/<int:pk>/edit/', PurchaseOrderUpdateView.as_view(), name='po-edit'),
    path('purchase-orders/<int:pk>/receive/', PurchaseOrderReceiveView.as_view(), name='po-receive'),

    # Sales Orders
    path('sales-orders/', SalesOrderListView.as_view(), name='so-list'),
    path('sales-orders/create/', SalesOrderCreateView.as_view(), name='so-create'),
    path('sales-orders/<int:pk>/edit/', SalesOrderUpdateView.as_view(), name='so-edit'),
    path('sales-orders/<int:pk>/complete/', SalesOrderCompleteView.as_view(), name='so-complete'),
]
