from django.db import models
from django.contrib.auth.models import User
from ProductsApp.models import Products
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.core.exceptions import ValidationError

# Create your models here.

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"
        
    def get_total_price(self):
        """Calculate the total price of all items in the cart"""
        return sum(item.get_total() for item in self.items.all())
        
    def get_total_items(self):
        """Get the total number of items in the cart"""
        return sum(item.quantity for item in self.items.all())
    
    def clear(self):
        """Remove all items from the cart"""
        self.items.all().delete()
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_added']
        unique_together = ('cart', 'product')  # Prevent duplicate products in cart
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"
    
    def get_total(self):
        """Calculate total price for this item"""
        return self.product.price * self.quantity

    @property
    def price(self):
        """Get current product price"""
        return self.product.price
    
    def clean(self):
        """Validate that quantity doesn't exceed available stock"""
        if self.quantity > self.product.stock:
            raise ValidationError(f"Cannot add {self.quantity} items. Only {self.product.stock} in stock.")
        
    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        self.clean()
        super().save(*args, **kwargs)
        
@receiver(post_save, sender=User)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    """Create a new cart when a user is created"""
    if created:
        Cart.objects.create(user=instance)
