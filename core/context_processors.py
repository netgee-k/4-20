from django.conf import settings

def site_settings(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'BITCOIN_WALLET_ADDRESS': settings.BITCOIN_WALLET_ADDRESS,
        'COMMISSION_RATE': settings.COMMISSION_RATE * 100,
    }
