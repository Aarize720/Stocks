from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import models
from django.forms import inlineformset_factory
import django.forms as forms
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView, View

from inventory.models import Supplier, Product, Location, InventoryItem, PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
from .forms import SignUpForm, SupplierForm, ProductForm, LocationForm, InventoryItemForm, PurchaseOrderItemInlineForm, SalesOrderItemInlineForm, AdjustInventoryForm


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('web:dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Votre compte a été créé avec succès.')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'web/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        low_stock = InventoryItem.objects.filter(quantity__lte=models.F('reorder_threshold')).select_related('product', 'location')
        ctx['low_stock'] = low_stock[:20]
        ctx['counts'] = {
            'products': Product.objects.count(),
            'suppliers': Supplier.objects.count(),
            'locations': Location.objects.count(),
            'inventory_items': InventoryItem.objects.count(),
        }
        return ctx


# Generic CRUD views
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'web/suppliers_list.html'
    context_object_name = 'items'
    paginate_by = 20
    extra_context = {'model_name': 'Fournisseurs', 'create_url': reverse_lazy('web:supplier-create')}

    def get_queryset(self):
        qs = super().get_queryset().order_by('name')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:supplier-list')


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:supplier-list')


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'web/confirm_delete.html'
    success_url = reverse_lazy('web:supplier-list')


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'web/products_list.html'
    context_object_name = 'items'
    paginate_by = 20
    extra_context = {'model_name': 'Produits', 'create_url': reverse_lazy('web:product-create')}

    def get_queryset(self):
        qs = super().get_queryset().order_by('sku')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(models.Q(sku__icontains=q) | models.Q(name__icontains=q))
        return qs


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:product-list')


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:product-list')


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'web/confirm_delete.html'
    success_url = reverse_lazy('web:product-list')


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'web/locations_list.html'
    context_object_name = 'items'
    paginate_by = 20
    extra_context = {'model_name': 'Entrepôts', 'create_url': reverse_lazy('web:location-create')}

    def get_queryset(self):
        qs = super().get_queryset().order_by('code')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(models.Q(code__icontains=q) | models.Q(name__icontains=q))
        return qs


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:location-list')


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:location-list')


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = 'web/confirm_delete.html'
    success_url = reverse_lazy('web:location-list')


class InventoryItemListView(LoginRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'web/inventory_list.html'
    context_object_name = 'items'
    paginate_by = 20
    extra_context = {'model_name': 'Stocks', 'create_url': reverse_lazy('web:inventory-create')}

    def get_queryset(self):
        qs = super().get_queryset().select_related('product', 'location').order_by('product__sku')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(models.Q(product__sku__icontains=q) | models.Q(product__name__icontains=q) | models.Q(location__code__icontains=q))
        return qs


class InventoryItemCreateView(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:inventory-list')


class InventoryItemUpdateView(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'web/generic_form.html'
    success_url = reverse_lazy('web:inventory-list')


class InventoryItemDeleteView(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'web/confirm_delete.html'
    success_url = reverse_lazy('web:inventory-list')


class InventoryAdjustView(LoginRequiredMixin, View):
    def get(self, request, pk):
        it = get_object_or_404(InventoryItem, pk=pk)
        form = AdjustInventoryForm()
        return render(request, 'web/inventory_adjust.html', {'form': form, 'item': it})

    def post(self, request, pk):
        it = get_object_or_404(InventoryItem, pk=pk)
        form = AdjustInventoryForm(request.POST)
        if form.is_valid():
            delta = form.cleaned_data['delta']
            from inventory.models import adjust_stock
            adjust_stock(it.product, it.location, delta)
            messages.success(request, f"Stock ajusté de {delta} pour {it.product.sku} @ {it.location.code}")
            return redirect('web:inventory-list')
        return render(request, 'web/inventory_adjust.html', {'form': form, 'item': it})


# Purchase Orders
class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'web/purchaseorders_list.html'
    context_object_name = 'items'
    paginate_by = 20
    extra_context = {'model_name': "Bons d'achat", 'create_url': reverse_lazy('web:po-create')}

    def get_queryset(self):
        qs = super().get_queryset().select_related('supplier', 'receive_location').order_by('-created_at')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(models.Q(reference__icontains=q) | models.Q(supplier__name__icontains=q))
        return qs


class PurchaseOrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        po = PurchaseOrder()
        form = forms.modelform_factory(PurchaseOrder, fields=['supplier', 'reference', 'expected_date', 'receive_location'])(instance=po)
        ItemFormSet = inlineformset_factory(PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemInlineForm, extra=3, can_delete=True)
        formset = ItemFormSet(instance=po)
        return render(request, 'web/purchaseorder_form.html', {'form': form, 'formset': formset, 'title': "Créer un bon d'achat"})

    def post(self, request):
        po = PurchaseOrder()
        Form = forms.modelform_factory(PurchaseOrder, fields=['supplier', 'reference', 'expected_date', 'receive_location'])
        ItemFormSet = inlineformset_factory(PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemInlineForm, extra=0, can_delete=True)
        form = Form(request.POST, instance=po)
        formset = ItemFormSet(request.POST, instance=po)
        if form.is_valid() and formset.is_valid():
            po = form.save()
            formset.instance = po
            formset.save()
            messages.success(request, "Bon d'achat créé")
            return redirect('web:po-list')
        return render(request, 'web/purchaseorder_form.html', {'form': form, 'formset': formset, 'title': "Créer un bon d'achat"})


class PurchaseOrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        Form = forms.modelform_factory(PurchaseOrder, fields=['supplier', 'reference', 'expected_date', 'receive_location', 'status'])
        ItemFormSet = inlineformset_factory(PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemInlineForm, extra=1, can_delete=True)
        form = Form(instance=po)
        formset = ItemFormSet(instance=po)
        return render(request, 'web/purchaseorder_form.html', {'form': form, 'formset': formset, 'title': f"Modifier PO #{po.id}"})

    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        Form = forms.modelform_factory(PurchaseOrder, fields=['supplier', 'reference', 'expected_date', 'receive_location', 'status'])
        ItemFormSet = inlineformset_factory(PurchaseOrder, PurchaseOrderItem, form=PurchaseOrderItemInlineForm, extra=0, can_delete=True)
        form = Form(request.POST, instance=po)
        formset = ItemFormSet(request.POST, instance=po)
        if form.is_valid() and formset.is_valid():
            po = form.save()
            formset.save()
            messages.success(request, "Bon d'achat mis à jour")
            return redirect('web:po-list')
        return render(request, 'web/purchaseorder_form.html', {'form': form, 'formset': formset, 'title': f"Modifier PO #{po.id}"})


class PurchaseOrderReceiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            po.receive()
            messages.success(request, "Stock réceptionné et PO marqué comme reçu")
        except Exception as e:
            messages.error(request, f"Erreur: {e}")
        return redirect('web:po-list')


# Sales Orders
class SalesOrderListView(LoginRequiredMixin, ListView):
    model = SalesOrder
    template_name = 'web/salesorders_list.html'
    context_object_name = 'items'
    paginate_by = 20
    extra_context = {'model_name': 'Commandes clients', 'create_url': reverse_lazy('web:so-create')}

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(models.Q(reference__icontains=q) | models.Q(customer_name__icontains=q))
        return qs


class SalesOrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        so = SalesOrder()
        Form = forms.modelform_factory(SalesOrder, fields=['reference', 'customer_name', 'ship_from'])
        ItemFormSet = inlineformset_factory(SalesOrder, SalesOrderItem, form=SalesOrderItemInlineForm, extra=3, can_delete=True)
        form = Form(instance=so)
        formset = ItemFormSet(instance=so)
        return render(request, 'web/salesorder_form.html', {'form': form, 'formset': formset, 'title': "Créer une commande"})

    def post(self, request):
        so = SalesOrder()
        Form = forms.modelform_factory(SalesOrder, fields=['reference', 'customer_name', 'ship_from'])
        ItemFormSet = inlineformset_factory(SalesOrder, SalesOrderItem, form=SalesOrderItemInlineForm, extra=0, can_delete=True)
        form = Form(request.POST, instance=so)
        formset = ItemFormSet(request.POST, instance=so)
        if form.is_valid() and formset.is_valid():
            so = form.save()
            formset.instance = so
            formset.save()
            messages.success(request, "Commande créée")
            return redirect('web:so-list')
        return render(request, 'web/salesorder_form.html', {'form': form, 'formset': formset, 'title': "Créer une commande"})


class SalesOrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        so = get_object_or_404(SalesOrder, pk=pk)
        Form = forms.modelform_factory(SalesOrder, fields=['reference', 'customer_name', 'ship_from', 'status'])
        ItemFormSet = inlineformset_factory(SalesOrder, SalesOrderItem, form=SalesOrderItemInlineForm, extra=1, can_delete=True)
        form = Form(instance=so)
        formset = ItemFormSet(instance=so)
        return render(request, 'web/salesorder_form.html', {'form': form, 'formset': formset, 'title': f"Modifier SO #{so.id}"})

    def post(self, request, pk):
        so = get_object_or_404(SalesOrder, pk=pk)
        Form = forms.modelform_factory(SalesOrder, fields=['reference', 'customer_name', 'ship_from', 'status'])
        ItemFormSet = inlineformset_factory(SalesOrder, SalesOrderItem, form=SalesOrderItemInlineForm, extra=0, can_delete=True)
        form = Form(request.POST, instance=so)
        formset = ItemFormSet(request.POST, instance=so)
        if form.is_valid() and formset.is_valid():
            so = form.save()
            formset.save()
            messages.success(request, "Commande mise à jour")
            return redirect('web:so-list')
        return render(request, 'web/salesorder_form.html', {'form': form, 'formset': formset, 'title': f"Modifier SO #{so.id}"})


class SalesOrderCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        so = get_object_or_404(SalesOrder, pk=pk)
        try:
            so.complete()
            messages.success(request, "Commande complétée et stock décrémenté")
        except Exception as e:
            messages.error(request, f"Erreur: {e}")
        return redirect('web:so-list')

from django.shortcuts import render

# Create your views here.
