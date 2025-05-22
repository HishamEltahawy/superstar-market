from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ReviewsApp.models import Reviews
from ReviewsApp.serializers import SzReview
from OrdersApp.models import Order
from .serializers import * 
from ProductsApp.models import Products

# Create your views here.


class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        user = request.user
        data = request.data

        if data['rating'] > 5 or data['rating'] < 1:
            return Response({"Error": "Please rate between 1:5"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has purchased the product
        has_purchased = Order.objects.filter(
            user=user, 
            items__product=product,
            status='Delivered'
        ).exists()

        if not has_purchased:
            return Response({'error': 'You can only review products you have purchased and received.'}, status=status.HTTP_403_FORBIDDEN)

        # Check for existing review
        if product.reviews.filter(user=user).exists():
            return Response({'error': 'You have already reviewed this product'}, status=status.HTTP_400_BAD_REQUEST)
 
        serializer = SzReview(data=data)
        if serializer.is_valid():
            serializer.save(user=user, product=product)
            return Response({'message': 'Review added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewsView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        reviews = product.reviews.all()
        serializer = SzReview(reviews, many=True)
        return Response({'reviews': serializer.data})

class ReviewDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        review = get_object_or_404(Reviews, id=pk)
        if review.user != request.user:
            return Response({'error': 'You do not have permission to delete this review'}, status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response({'message': 'Review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

