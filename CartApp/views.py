from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction
from .models import CartItem
from .serializers import (
    CartSerializer, CartItemSerializer,)


# Create your views here.
class CartView(APIView):
    """View for retrieving and managing the user's shopping cart"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get the current user's cart with all items"""
        cart = request.user.cart
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def delete(self, request):
        """Clear all items from the cart"""
        cart = request.user.cart
        cart.clear()
        return Response({"message": "Cart cleared successfully"}, status=status.HTTP_200_OK)

class CartItemView(APIView):
    """View for managing individual cart items"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Add item to cart or update quantity if it exists"""
        try:
            with transaction.atomic():
                # Validate request data
                if not request.data.get('product_id'):
                    return Response(
                        {"error": "Product ID is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                quantity = int(request.data.get('quantity', 1))
                if quantity <= 0:
                    return Response(
                        {"error": "Quantity must be greater than zero"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Initialize serializer with request context
                serializer = CartItemSerializer(
                    data=request.data,
                    context={'request': request}
                )
                if serializer.is_valid():
                    # Save cart item within transaction
                    serializer.save()
                    
                    # Return updated cart data
                    cart_serializer = CartSerializer(request.user.cart)
                    return Response(
                        cart_serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValueError:
            return Response(
                {"error": "Invalid quantity value"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, product_id):
        """Update the quantity of an item in the cart"""
        cart = request.user.cart
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
            new_quantity = request.data.get('quantity', 0)
            
            if new_quantity <= 0:
                return Response(
                    {"error": "Quantity must be greater than zero"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if new_quantity > cart_item.product.stock:
                return Response(
                    {"error": "Quantity exceeds available stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item.quantity = new_quantity
            cart_item.save()
            
            # Return the updated cart
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Product not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, product_id):
        """Remove an item from the cart"""
        cart = request.user.cart
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)
            cart_item.delete()
            
            # Return the updated cart
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Product not found in cart"}, 
                status=status.HTTP_404_NOT_FOUND
            )
