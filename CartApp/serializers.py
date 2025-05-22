from rest_framework import serializers
from .models import Cart, CartItem
from ProductsApp.models import Products

from ReviewsApp.models import Reviews
from OrdersApp.models import Order, OrderItem
from OrdersApp.serializers import OrderSerializer





class ProductMiniSerializer(serializers.ModelSerializer):
    """Minimal Product representation for cart/order items"""
    class Meta:
        model = Products
        fields = ['id', 'name', 'image', 'price', 'stock']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items with product information"""
    product = ProductMiniSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True, required=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'date_added', 'total_price']
        read_only_fields = ['id', 'date_added', 'product', 'total_price']
    
    def get_total_price(self, obj):
        return obj.get_total()
    
    def validate(self, data):
        """Validate product exists and has sufficient stock"""
        try:
            product = Products.objects.get(id=data['product_id'])
            if data['quantity'] > product.stock:
                raise serializers.ValidationError(
                    f"Cannot add {data['quantity']} items. Only {product.stock} in stock."
                )
        except Products.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        return data
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = Products.objects.get(id=product_id)
        
        # Get or create cart item
        cart = self.context['request'].user.cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': validated_data['quantity']}
        )
        
        # Update quantity if item already exists
        if not created:
            cart_item.quantity = validated_data['quantity']
            cart_item.save()
            
        return cart_item


class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart with item details"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'updated_at', 'is_active', 'items', 'total_price', 'total_items']
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    
    def get_total_items(self, obj):
        return obj.get_total_items()

