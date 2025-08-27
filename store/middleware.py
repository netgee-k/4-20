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

        # Try to get client by session_id first
        try:
            client = AnonymousClient.objects.get(session_id=session_id)
        except AnonymousClient.DoesNotExist:
            # Get client IP
            ip_address = self.get_client_ip(request)
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()

            # Create new client
            client = AnonymousClient.objects.create(
                session_id=session_id,
                ip_hash=ip_hash,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                created_at=timezone.now(),
                last_active=timezone.now()
            )

        # Update last_active (safe, does not touch unique fields)
        client.last_active = timezone.now()
        client.save(update_fields=['last_active'])

        # Store in request
        request.anonymous_client = client
        request.client_ip = self.get_client_ip(request)

        # Get or create cart
        cart, _ = Cart.objects.get_or_create(
            client=client,
            is_active=True
        )
        request.cart = cart

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
