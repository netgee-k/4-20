# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Product, Order, BitcoinWallet
import json
from django.utils import timezone
from datetime import timedelta

def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            # For now, use a mock Bitcoin address
            # In production, generate a new address from your wallet
            mock_address = "tb1qexampletestnetaddress"  # Replace with real address generation
            
            order = Order.objects.create(
                product=product,
                bitcoin_address=mock_address,
                amount_btc=product.price_btc,
                amount_sats=product.get_price_sats(),
                status='pending'
            )
            
            qr_code = order.generate_qr_code()
            
            return JsonResponse({
                'success': True,
                'order_id': order.order_id,
                'bitcoin_address': order.bitcoin_address,
                'amount_btc': float(order.amount_btc),
                'amount_sats': order.amount_sats,
                'qr_code': qr_code,
                'expires_at': order.expires_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def order_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    # Mock payment check - replace with real blockchain monitoring
    # For now, we'll simulate payment after 2 minutes
    from datetime import datetime, timedelta
    mock_paid = (datetime.now() - order.created_at.replace(tzinfo=None)) > timedelta(minutes=2)
    
    if mock_paid and order.status == 'pending':
        order.status = 'paid'
        order.tx_hash = 'mock_transaction_hash_12345'
        order.save()
    
    return JsonResponse({
        'order_id': order.order_id,
        'status': order.status,
        'amount_btc': float(order.amount_btc),
        'bitcoin_address': order.bitcoin_address,
        'tx_hash': order.tx_hash,
        'expired': order.is_expired()
    })

def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    qr_code = order.generate_qr_code()
    
    return render(request, 'store/order_detail.html', {
        'order': order,
        'qr_code': qr_code,
        'bitcoin_uri': f"bitcoin:{order.bitcoin_address}?amount={order.amount_btc}"
    })
