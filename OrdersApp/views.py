from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import  Order
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    ProductReviewSerializer)

class OrderListView(ListAPIView):
    """View for listing user orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return orders for current user or all orders for admin"""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

class OrderDetailView(RetrieveAPIView):
    """View for retrieving order details"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ensure users can only see their own orders unless admin"""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class CreateOrderView(APIView):
    """View for creating a new order from cart items"""
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Create order from cart items"""
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            order = serializer.save()
            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateOrderStatusView(APIView):
    """View for updating order status (admin only)"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @transaction.atomic
    def put(self, request, pk):
        """Update order status with proper validation and transaction handling"""
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderStatusUpdateSerializer(order, data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            # Validate status transition
            current_status = order.status
            valid_transition = self._is_valid_status_transition(current_status, new_status)
            if not valid_transition:
                return Response(
                    {"error": f"Invalid status transition from '{current_status}' to '{new_status}'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save with transaction handling
            serializer.save()
            
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _is_valid_status_transition(self, current_status, new_status):
        """Validate if the status transition is allowed"""
        # Define valid transitions
        valid_transitions = {
            'Pending': ['Processing', 'Shipped', 'Cancelled'],  # Added 'Shipped' as valid transition
            'Processing': ['Shipped', 'Cancelled'],
            'Shipped': ['Delivered', 'Cancelled'],
            'Delivered': [],  # No further transitions from Delivered
            'Cancelled': []   # No further transitions from Cancelled
        }
        
        # Check if the transition is valid
        return new_status in valid_transitions.get(current_status, [])


class CancelOrderView(APIView):
    """View for cancelling an order"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Cancel order if it's in a cancellable state"""
        user = request.user
        query = Order.objects.filter(pk=pk)
        
        # Only let admins cancel any order
        if not user.is_staff:
            query = query.filter(user=user)
            
        order = get_object_or_404(query)
        
        if not order.can_cancel():
            return Response(
                {"error": "This order cannot be cancelled in its current state"},
                status=status.HTTP_400_BAD_REQUEST
            )
      
        order.status = 'Cancelled'
        order.save()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )


class OrderStatusView(APIView):
    """View for retrieving and updating order status"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        """Retrieve the status of a specific order"""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            return Response({"status": order.status}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, order_id):
        """Update the status of a specific order"""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            new_status = request.data.get("status")
            if new_status not in dict(Order.ORDER_STATUS_CHOICES):
                return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

            order.status = new_status
            order.save()
            return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

class CreateProductReviewView(APIView):
    """View for creating product reviews from delivered orders"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a product review for a delivered order item"""
        serializer = ProductReviewSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                {"message": "Review created successfully"},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
