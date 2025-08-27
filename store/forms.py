# store/forms.py

from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    delivery_address = forms.CharField(
        label="Delivery Address",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Enter your delivery address"})
    )

    class Meta:
        model = Order
        fields = ['product', 'quantity', 'delivery_address']  # ✅ include address
