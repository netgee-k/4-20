#!/bin/bash

# ----------------------------
# 420 Marketplace Startup Script
# ----------------------------

# ASCII Art
echo "          _____"
echo "        /    /                                       .-''-."
echo "       /    /                                      .' .-.  )"
echo "      /    /                  ,.--.               / .'  / /"
echo "     /    /                  //    \             (_/   / /                   .-''\` ''-."
echo "    /    /  __               \\    /                  / /                  .'          '."
echo "   /    /  |  |               \`'--'                  / /                  /              \`"
echo "  /    '   |  |               ,.--.                 . '                  '                '"
echo " /    '----|  |---.          //    \               / /    _.-')          |         .-.    |"
echo "/          |  |   |          \\    /             .' '  _.'.-''           .        |   |   ."
echo "'----------|  |---'           \`'--'             /  /.-'_.'                .       '._.'  /"
echo "           |  |                                /    _.'                    '._         .'"
echo "          /____\                              ( _.-'                          '-....-'\`"
echo ""
echo "              🚀 420 MARKETPLACE STARTUP 🚀"
echo "_________________________________________________________"

# ----------------------------
# Helper Functions
# ----------------------------
error_exit() {
    echo "❌ ERROR: $1"
    exit 1
}

success_msg() {
    echo "✅ $1"
}

# ----------------------------
# Port Setup
# ----------------------------
read -p "🌐 Enter port number (default: 420): " PORT
PORT=${PORT:-420}

echo "🔍 Checking port $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is in use. Attempting to free it..."
    sudo fuser -k $PORT/tcp 2>/dev/null || true
    sleep 2
fi

# ----------------------------
# Virtual Environment
# ----------------------------
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv || error_exit "Failed to create virtual environment"
    success_msg "Virtual environment created"
else
    echo "🐍 Virtual environment already exists"
fi

source venv/bin/activate || error_exit "Failed to activate virtual environment"

# ----------------------------
# Dependencies
# ----------------------------
if [ ! -f "requirements_installed.flag" ]; then
    echo "📦 Installing requirements..."
    [ ! -f "mahitaji.txt" ] && pip freeze > mahitaji.txt
    pip install -r mahitaji.txt || error_exit "Failed to install requirements"
    touch requirements_installed.flag
    success_msg "Requirements installed"
else
    echo "📦 Requirements already installed"
fi

# ----------------------------
# Database
# ----------------------------
echo "🗄️  Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
success_msg "Database migrations completed"

# ----------------------------
# Superuser
# ----------------------------
echo "👤 Checking admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@420.com', 'admin420')
    print("Superuser created: admin / admin420")
else:
    print("Admin user already exists")
EOF

# ----------------------------
# Static Files
# ----------------------------
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput
success_msg "Static files ready"

# ----------------------------
# Seed Data
# ----------------------------
echo "🎯 Creating initial data..."
export PORT
python manage.py shell << EOF
from store.models import Product, DeliveryStation
from django.contrib.sites.models import Site
import os

PORT = os.environ.get('PORT', '420')

# Ensure default site
site, created = Site.objects.get_or_create(
    id=1,
    defaults={'domain': f'localhost:{PORT}', 'name': '420 Marketplace'}
)
if created:
    print("Default site configured")

# Sample products
if not Product.objects.exists():
    products = [
        {'name': 'Anonymous VPN Service', 'description': 'High-speed encrypted VPN', 'price_btc': '0.0025', 'is_active': True},
        {'name': 'Secure Messaging', 'description': 'End-to-end encrypted chats', 'price_btc': '0.0018', 'is_active': True},
        {'name': 'Privacy Guide', 'description': 'Complete anonymity tutorial', 'price_btc': '0.0009', 'is_active': True},
        {'name': 'Bitcoin Mixer', 'description': 'Coin anonymization service', 'price_btc': '0.0035', 'is_active': True},
    ]
    for data in products:
        Product.objects.create(**data)
    print("Sample products created")

# Delivery stations
if not DeliveryStation.objects.exists():
    stations = [
        {'name': 'Downtown Dead Drop', 'location': 'Central Station Locker #42', 'is_active': True},
        {'name': 'Northside Pickup', 'location': '24/7 Automated Kiosk', 'is_active': True},
        {'name': 'Digital Delivery', 'location': 'Instant Online Access', 'is_active': True},
    ]
    for data in stations:
        DeliveryStation.objects.create(**data)
    print("Delivery stations ready")
EOF

# ----------------------------
# Startup Info
# ----------------------------
echo ""
echo "_________________________________________________________"
echo "🎉 420 MARKETPLACE READY!"
echo "🌐 Local URL: http://localhost:$PORT/"
echo "⚡ Admin Panel: http://localhost:$PORT/admin/"
echo "🔑 Admin Login: admin / admin420"
echo "🛒 Store Front: http://localhost:$PORT/store/products/"
echo ""
echo "🚀 Starting server... Press Ctrl+C to stop"
echo "_________________________________________________________"

python manage.py runserver 0.0.0.0:$PORT
