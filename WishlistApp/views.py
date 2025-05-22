from django.shortcuts import render
from .models import Wishlist
from ProductsApp.models import Products
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# Create your views here.
class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            products = wishlist.products.all()
            product_data = [
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "category": product.category.name if product.category else None,
                }
                for product in products
            ]
            return Response({"wishlist": product_data}, status=status.HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response({"wishlist": []}, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=product_id)
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            wishlist.products.add(product)
            return Response({"message": "Product added to wishlist."}, status=status.HTTP_201_CREATED)
        except Products.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=product_id)
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist.products.remove(product)
            return Response({"message": "Product removed from wishlist."}, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Wishlist.DoesNotExist:
            return Response({"error": "Wishlist not found."}, status=status.HTTP_404_NOT_FOUND)

