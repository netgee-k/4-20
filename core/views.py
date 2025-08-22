from django.shortcuts import render
from store.models import Product  # Add this import

def home(request):
    # Get featured products from the store
    featured_products = Product.objects.filter(is_active=True)[:3]
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'core/home.html', context)
