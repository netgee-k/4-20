from django.db import models
from django.conf import settings
import hashlib
import time
import qrcode
import io
import base64
from django.core.files.base import ContentFile

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_btc = models.DecimalField(max_digits=18, decimal_places=8)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_price_sats(self):
        return int(self.price_btc * 100000000)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=64, unique=True)
    bitcoin_address = models.CharField(max_length=100, blank=True)
    amount_btc = models.DecimalField(max_digits=18, decimal_places=8)
    amount_sats = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tx_hash = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def generate_order_id(self):
        timestamp = str(time.time())
        return hashlib.sha256(timestamp.encode()).hexdigest()[:16]
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        if not self.expires_at:
            from django.utils import timezone
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        bitcoin_uri = f"bitcoin:{self.bitcoin_address}?amount={self.amount_btc}"
        qr.add_data(bitcoin_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

class BitcoinWallet(models.Model):
    address = models.CharField(max_length=100, unique=True)
    private_key = models.CharField(max_length=100)  # Encrypt this in production!
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
