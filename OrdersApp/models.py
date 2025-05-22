from django.db import models
from django.contrib.auth.models import User
from ProductsApp.models import Products
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from CartApp.models import Cart, CartItem

@receiver(pre_save, sender='OrdersApp.Order')
def update_delivered_timestamp(sender, instance, **kwargs):
    """Set delivered_at timestamp when order status changes to Delivered"""
    if instance.pk:  # if this is an update, not a new creation
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.status != 'Delivered' and instance.status == 'Delivered':
                instance.delivered_at = timezone.now()
        except sender.DoesNotExist:
            pass

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('CARD', 'Credit/Debit Card'),
        ('WALLET', 'Digital Wallet'),
        ('BANK', 'Bank Transfer'),
    ]
    
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='COD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    delivered_at = models.DateTimeField(null=True, blank=True)
    # Cart to Order relationship - optional now as we handle conversion in views
    from_cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # Address information
    shipping_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    phone_no = models.CharField(max_length=20, blank=True)
    def calculate_total(self):
        """Recalculate order total from order items"""
        return sum(item.get_total() for item in self.items.all())
    
    def update_total(self):
        """Update the total_amount field based on items"""
        self.total_amount = self.calculate_total()
        self.save()
    
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in ['Pending', 'Processing']
    
    def can_be_reviewed(self):
        """Check if items in this order can be reviewed"""
        return self.status == 'Delivered' and self.delivered_at is not None

    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Unknown'}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product_name = models.CharField(max_length=200)  # Store name at time of purchase
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase
    reviewed = models.BooleanField(default=False)  # Track if item has been reviewed
    
    # Optional link to original cart item
    original_cart_item = models.OneToOneField(
        CartItem, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='order_item'
    )

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order {self.order.id}"
        
    def get_total(self):
        """Calculate total price for this item"""
        return self.price * self.quantity
    
    def can_review(self):
        """Check if this item can be reviewed"""
        return (not self.reviewed and 
                self.order.status == 'Delivered' and 
                self.order.delivered_at is not None)


@receiver(post_save, sender=OrderItem)
def track_product_stock(sender, instance, created, **kwargs):
    """Update product stock when order item is created"""
    if created and instance.product:
        product = instance.product
        product.stock = max(0, product.stock - instance.quantity)
        product.save()


@receiver(post_save, sender=Order)
def handle_order_cancellation(sender, instance, **kwargs):
    """Return products to stock if order is cancelled"""
    if instance.status == 'Cancelled':
        for item in instance.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
