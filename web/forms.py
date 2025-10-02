from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from inventory.models import Supplier, Product, Location, InventoryItem, PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem


class AdjustInventoryForm(forms.Form):
    delta = forms.IntegerField(label="Ajustement (peut être négatif)")
    reason = forms.CharField(label="Raison", required=False)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'address', 'website']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'unit_cost', 'unit_price', 'supplier', 'is_active', 'track_inventory']


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['code', 'name', 'address']


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['product', 'location', 'quantity', 'reorder_threshold']


class PurchaseOrderItemInlineForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'quantity', 'unit_cost']


class SalesOrderItemInlineForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ['product', 'quantity', 'unit_price']