# store/management/commands/fix_order_relations.py
from django.core.management.base import BaseCommand
from store.models import Order

class Command(BaseCommand):
    help = 'Fix order relationships by ensuring all orders have session_id'
    
    def handle(self, *args, **options):
        orders = Order.objects.filter(session_id='')
        for order in orders:
            # Generate a session ID for orders that don't have one
            if not order.session_id:
                order.session_id = f"anon_{order.id}"
                order.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated {orders.count()} orders with session IDs')
        )
