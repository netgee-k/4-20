#!/bin/bash

# Your awesome ASCII art
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

# Function for error handling
error_exit() {
    echo "❌ ERROR: $1"
    exit 1
}

# Function for success messages
success_msg() {
    echo "✅ $1"
}

# Get port number
read -p "🌐 Enter port number (default: 420): " PORT
PORT=${PORT:-420}

# Check port availability
echo "🔍 Checking port $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is in use. Attempting to free it..."
    sudo fuser -k $PORT/tcp 2>/dev/null || true
    sleep 2
fi

# Check and create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv || error_exit "Failed to create virtual environment"
    success_msg "Virtual environment created"
else
    echo "🐍 Virtual environment already exists"
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate || error_exit "Failed to activate virtual environment"

# Install requirements
if [ ! -f "requirements_installed.flag" ]; then
    echo "📦 Installing requirements..."
    
    # Check if requirements file exists
    if [ ! -f "mahitaji.txt" ]; then
        echo "📝 Creating mahitaji.txt from current environment..."
        pip freeze > mahitaji.txt 2>/dev/null || echo "# Django marketplace requirements" > mahitaji.txt
    fi
    
    pip install -r mahitaji.txt || error_exit "Failed to install requirements"
    touch requirements_installed.flag
    success_msg "Requirements installed"
else
    echo "📦 Requirements already installed"
fi

# Database setup
echo "🗄️  Setting up database..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
success_msg "Database migrations completed"

# Create superuser if needed
echo "👤 Checking admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("Creating superuser...")
    User.objects.create_superuser('admin', 'admin@420.com', 'admin420')
    print("Superuser created: username=admin, password=admin420")
else:
    print("Admin user already exists")
EOF

# Collect static files
echo "📁 Preparing static files..."
python manage.py collectstatic --noinput
success_msg "Static files ready"

# Setup initial data
echo "🎯 Creating default data..."
python manage.py shell << EOF
from store.models import Product, DeliveryStation
from django.contrib.sites.models import Site

# Ensure default site
site, created = Site.objects.get_or_create(
    id=1,
    defaults={'domain': 'localhost:$PORT', 'name': '420 Marketplace'}
)
if created:
    print("Default site configured")

# Create sample products
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

# Create delivery stations
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

# Display startup info
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

# Run the server
python manage.py runserver 0.0.0.0:$PORT
