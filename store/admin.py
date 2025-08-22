# Register your models here.
from django.contrib import admin
from .models import Product, Order, BitcoinWallet

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_btc', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'product', 'amount_btc', 'status', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(BitcoinWallet)
class BitcoinWalletAdmin(admin.ModelAdmin):
    list_display = ['address', 'balance', 'is_active', 'created_at']
