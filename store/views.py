from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, OrderItem, Cart, CartItem, EncryptedMessage
import json
from django.utils import timezone
from datetime import timedelta
import socket

# ----------------------------
# Product Views
# ----------------------------
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'store/product_list.html', {
        'products': products,
        'cart_count': request.cart.get_item_count() if hasattr(request, 'cart') else 0
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart_count': request.cart.get_item_count() if hasattr(request, 'cart') else 0
    })

# ----------------------------
# Cart Views
# ----------------------------
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))

            product = get_object_or_404(Product, id=product_id, is_active=True)
            cart = request.cart

            # Check stock and limits
            if quantity > product.stock_quantity:
                return JsonResponse({'success': False, 'error': 'Not enough stock'})
            if quantity > product.max_per_order:
                return JsonResponse({'success': False, 'error': f'Max {product.max_per_order} per order'})

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({
                'success': True,
                'message': 'Added to cart',
                'cart_count': cart.items.count(),
                'cart_total': float(cart.get_total_btc())
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def cart_view(request):
    cart = request.cart
    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart.items.all(),
        'cart_total': cart.get_total_btc(),
        'cart_count': cart.get_item_count()
    })

@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')

            cart = request.cart
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
            cart_item.delete()

            return JsonResponse({
                'success': True,
                'message': 'Removed from cart',
                'cart_count': cart.items.count(),
                'cart_total': float(cart.get_total_btc())
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# ----------------------------
# Order Views
# ----------------------------
@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            delivery_option = data.get('delivery_option', 'digital')

            cart = request.cart
            client = request.anonymous_client

            if cart.items.count() == 0:
                return JsonResponse({'success': False, 'error': 'Cart is empty'})

            # Calculate totals
            total_btc = cart.get_total_btc()
            total_sats = int(total_btc * 100_000_000)

            # Create order
            order = Order.objects.create(
                client=client,
                bitcoin_address="tb1qexampletestnetaddress",
                bitcoin_amount=total_btc,   # ✅ updated field
                amount_sats=total_sats,
                delivery_option=delivery_option,
                status='pending',
                ip_hash=client.ip_hash
            )

            # Add order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    price_btc=cart_item.product.price_btc
                )

            # Clear cart and create new one
            cart.items.all().delete()
            cart.is_active = False
            cart.save()
            new_cart = Cart.objects.create(client=client)
            request.cart = new_cart

            qr_code = order.generate_qr_code() if hasattr(order, 'generate_qr_code') else None

            return JsonResponse({
                'success': True,
                'order_id': str(order.order_number),
                'bitcoin_address': order.bitcoin_address,
                'bitcoin_amount': float(order.bitcoin_amount),
                'amount_sats': order.amount_sats,
                'qr_code': qr_code,
                'expires_at': getattr(order, 'expires_at', None),
                'delivery_option': order.delivery_option
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def order_status(request, order_id):
    order = get_object_or_404(Order, order_number=order_id)

    # Mock payment check
    mock_paid = (timezone.now() - order.created_at) > timedelta(minutes=2)

    if mock_paid and order.status == 'pending':
        order.status = 'paid'
        order.tx_hash = getattr(order, 'tx_hash', 'mock_tx_hash_12345')
        order.save()

    return JsonResponse({
        'order_id': str(order.order_number),
        'status': order.status,
        'bitcoin_amount': float(order.bitcoin_amount),
        'bitcoin_address': order.bitcoin_address,
        'tx_hash': getattr(order, 'tx_hash', ''),
        'expired': getattr(order, 'is_expired', lambda: False)(),
        'delivery_option': order.delivery_option
    })

def order_detail(request, order_id):
    order = get_object_or_404(Order, order_number=order_id)
    qr_code = order.generate_qr_code() if hasattr(order, 'generate_qr_code') else None

    return render(request, 'store/order_detail.html', {
        'order': order,
        'qr_code': qr_code,
        'bitcoin_uri': f"bitcoin:{order.bitcoin_address}?amount={order.bitcoin_amount}",
        'cart_count': request.cart.get_item_count() if hasattr(request, 'cart') else 0
    })

# ----------------------------
# Client Info
# ----------------------------
def client_info(request):
    client = request.anonymous_client
    ip_address = getattr(request, 'client_ip', None)

    # Simple Tor detection
    is_tor = False
    if ip_address:
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            is_tor = '.tor.' in hostname.lower()
        except:
            pass

    return JsonResponse({
        'client_id': client.get_anonymous_identifier(),
        'ip_address': ip_address,
        'ip_hash': client.ip_hash[:8] + '••••••••' if client.ip_hash else "N/A",
        'is_tor': is_tor,
        'session_active': True,
        'orders_count': Order.objects.filter(client=client).count(),
        'cart_count': request.cart.get_item_count() if hasattr(request, 'cart') else 0
    })

# ----------------------------
# Messaging
# ----------------------------
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            message_type = data.get('message_type', 'order_update')
            content = data.get('content', '')

            order = get_object_or_404(Order, order_number=order_id)
            client = request.anonymous_client

            if order.client != client:
                return JsonResponse({'success': False, 'error': 'Not authorized'})

            message = EncryptedMessage.objects.create(
                order=order,
                client=client,
                message_type=message_type
            )
            message.encrypt_message(content)
            message.save()

            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'expires_at': message.expires_at.isoformat()
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
