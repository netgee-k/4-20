# core/views.py
from django.shortcuts import render
from store.models import Product, AnonymousClient, Cart
import hashlib
import uuid

def get_client_ip(request):
    """Get client IP from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip

def get_ip_hash(ip):
    """Hash the IP address to store safely."""
    return hashlib.sha256(ip.encode()).hexdigest()

def home(request):
    # --- Handle Anonymous Client ---
    ip = get_client_ip(request)
    ip_hash = get_ip_hash(ip)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Get or create the anonymous client safely
    client, created = AnonymousClient.objects.get_or_create(
        ip_hash=ip_hash,
        defaults={
            'user_agent': user_agent,
            'session_id': f"session_{uuid.uuid4().hex[:8]}"
        }
    )

    # --- Handle Cart for the client ---
    cart, cart_created = Cart.objects.get_or_create(
        client=client,
        defaults={'session_id': f"cart_{uuid.uuid4().hex[:8]}"}
    )

    # --- Fetch featured products ---
    featured_products = Product.objects.filter(is_active=True)[:3]

    context = {
        'featured_products': featured_products,
        'client': client,
        'cart': cart,
    }

    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')
