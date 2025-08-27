# store/utils.py
import hashlib
from .models import AnonymousClient

def get_or_create_anonymous_client(request):
    # Get client IP (consider X-Forwarded-For for proxies)
    ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    # Get existing client or create a new one
    client, created = AnonymousClient.objects.get_or_create(
        ip_hash=ip_hash,
        defaults={'user_agent': request.META.get('HTTP_USER_AGENT', '')}
    )
    return client
