import os
from pathlib import Path
import environ

# Initialize environment
env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY', default='insecure-default-key-change-me')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1' , '172.29.119.43'])

# Applications
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'django.contrib.sites',  
    'store'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'marketplace_420.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'marketplace_420.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Custom settings
BITCOIN_WALLET_ADDRESS = env('BITCOIN_WALLET_ADDRESS', default='12345')
COMMISSION_RATE = env.float('COMMISSION_RATE', default=0.05)
SITE_NAME = env('SITE_NAME', default='420')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1





# Jazzmin Settings - Cyberpunk Dark Theme
JAZZMIN_SETTINGS = {
    # General
    "site_title": "Soko Huru",
    "site_header": "Soko Huru ", 
    "site_brand": "SOKO HURU'",
    "welcome_sign": "Welcome to Soko Huru",

 # Logo and branding
    "site_logo": "img/logo.png",  # Path to your logo
    "site_logo_classes": "img-circle",  # Optional: makes it circular
    
    # Favicon
    "site_icon": "img/logo.png",
    
    # Login page logo
    "login_logo": "img/logo.png",
    "login_logo_dark": "img/logo.png",
    
    # Logo style
    "site_logo_classes": "img-circle",  # Optional: circular style
    
    "copyright": "420 Marketplace",
    
    # Theme
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    
    # Layout
    "show_sidebar": True,
    "navigation_expanded": True,
    "related_modal_active": False,
    "show_ui_builder": True,
    
    # Menu Customization - Reorder and customize
    "order_with_respect_to": [
        "auth",
        "store",
        "store.Product",
        "store.Order", 
        "store.DeliveryStation",
        "store.AnonymousUser",
        "sites",
    ],
    
    # Top Menu
    "topmenu_links": [
        {"name": "🌐 View Site", "url": "/", "new_window": False},
        {"name": "🛒 Store", "url": "/store/products/", "new_window": False},
        {"model": "auth.user"},
        {"app": "store"},
    ],
    
    # Icons - Cyberpunk style
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-secret",
        "auth.Group": "fas fa-users",
        "store.Product": "fas fa-box",
        "store.Order": "fas fa-shopping-cart",
        "store.DeliveryStation": "fas fa-map-marker-alt",
        "store.AnonymousUser": "fas fa-user-ninja",
        "store.BitcoinWallet": "fas fa-bitcoin",
        "sites.Site": "fas fa-globe",
    },
    
    # Custom menus
    "custom_links": {
        "store": [{
            "permissions": ["store.view_order"]
        }]
    },
}

# Jazzmin UI Tweaks
JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
}
