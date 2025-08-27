from django.utils import timezone
from .models import AnonymousClient, Cart
import uuid
import hashlib

class AnonymousSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Create or get session ID
        if 'client_session_id' not in request.session:
            request.session['client_session_id'] = str(uuid.uuid4())
        
        session_id = request.session['client_session_id']
        
        # Get or create anonymous client
        client, created = AnonymousClient.objects.get_or_create(
            session_id=session_id,
            defaults={
                'created_at': timezone.now(),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
        
        if created:
            client.client_hash = client.generate_client_hash()
            client.save()
        
        # Get client IP and hash it
        ip_address = self.get_client_ip(request)
        client.ip_hash = client.hash_ip(ip_address)
        client.last_active = timezone.now()
        client.save()
        
        # Store in request
        request.anonymous_client = client
        request.client_ip = ip_address
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(
            client=client,
            is_active=True,
            defaults={'created_at': timezone.now()}
        )
        request.cart = cart
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
