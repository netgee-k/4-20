# store/admin.py
from django.contrib import admin
from .models import Product, Order, OrderItem, DeliveryStation, BitcoinWallet

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'email', 'status', 'list_products', 'total_amount', 'created_at', 'payment_confirmed']  # Added list_products here
    list_filter = ['status', 'payment_confirmed', 'created_at']
    search_fields = ['order_number', 'email', 'delivery_address']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'total_amount']
    inlines = [OrderItemInline]

    # Fixed method - uses the correct related name 'items'
    def list_products(self, obj):
        return ", ".join([f"{item.quantity}x {item.product.name}" for item in obj.items.all()])
    list_products.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'is_available']
    list_editable = ['price', 'quantity', 'is_available']
    search_fields = ['name']

@admin.register(DeliveryStation)
class DeliveryStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active']

@admin.register(BitcoinWallet)
class BitcoinWalletAdmin(admin.ModelAdmin):
    list_display = ['address', 'balance', 'last_checked']
    readonly_fields = ['last_checked']
