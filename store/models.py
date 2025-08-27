# store/models.py
from django.db import models
import uuid
import hashlib
from django.utils import timezone
from datetime import timedelta

# ----------------------------
# Product & Order Models
# ----------------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_btc = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    # Anonymous order identification
    session_id = models.CharField(max_length=100, blank=True, default='')
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Contact information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, default='')

    # Delivery information
    delivery_address = models.TextField()
    delivery_instructions = models.TextField(blank=True, default='')

    # Order details
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Bitcoin payment details
    bitcoin_address = models.CharField(max_length=100, blank=True, default='')
    bitcoin_amount = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    payment_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class DeliveryStation(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    instructions = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BitcoinWallet(models.Model):
    address = models.CharField(max_length=100, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address


# ----------------------------
# Anonymous Client & Cart
# ----------------------------
class AnonymousClient(models.Model):
    ip_hash = models.CharField(max_length=64, unique=True)
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=100, unique=True, default='temp_session')
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    def get_anonymous_identifier(self):
        return f"client_{self.id}_{self.ip_hash[:8]}"

    def __str__(self):
        return self.get_anonymous_identifier()


class Cart(models.Model):
    client = models.ForeignKey(
        AnonymousClient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'  # avoid name clash
    )
    session_id = models.CharField(max_length=100, unique=True, default='temp_session')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def get_item_count(self):
        return self.items.count()

    def get_total_btc(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart {self.session_id} - {self.client}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# ----------------------------
# Encrypted Messages
# ----------------------------
class EncryptedMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    client = models.ForeignKey(
        AnonymousClient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages'  # avoid name clash
    )
    message_type = models.CharField(max_length=50, default='order_update')
    encrypted_content = models.TextField()
    encryption_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(days=7))

    def encrypt_message(self, content):
        self.encrypted_content = f"encrypted_{content}_{self.created_at.timestamp()}"
        self.encryption_key = f"key_{hashlib.sha256(content.encode()).hexdigest()[:32]}"

    def __str__(self):
        return f"Message for Order #{self.order.order_number}"
