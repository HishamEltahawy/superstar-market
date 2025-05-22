from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from utils.recommendations import get_recommended_products
from django.shortcuts import get_object_or_404
from django.db.models import Min, Max
from .serializers import *
from .filters import ProductFilters
from .tasks import sleep
from AccountsApp.models import Profile
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers, vary_on_cookie


class ProductListView(APIView):
    
    @method_decorator(cache_page(60 * 20, key_prefix='product_list'))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get(self, request):
        products = Products.objects.all()
        serializer = SzProducts(products, many=True)
        import time
        time.sleep(5)
        return Response({'data': serializer.data})

class ProductDetailView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        serializer = SzProducts(product, many=False)
        return Response({'data': serializer.data})

class FilteredProductsView(APIView):
    def get(self, request):
        products = Products.objects.all()
        filterset = ProductFilters(request.GET, products)
        
        # Get aggregate data for filters
        price_range = products.aggregate(min=Min('price'), max=Max('price'))
        brands = products.values_list('brand', flat=True).distinct()
        categories = dict(Products.Categories.choices)
        
        # Apply filters
        filtered_products = filterset.qs
        
        serializer = SzProducts(filtered_products, many=True)
        return Response({
            'data': serializer.data,
            'metadata': {
                'total_count': filtered_products.count(),
                'price_range': price_range,
                'available_brands': list(brands),
                'available_categories': categories,
            }
        })

class FilteredProductsPaginatedView(APIView):
    def get(self, request):
        products = Products.objects.all()
        filterset = ProductFilters(request.GET, products)
        
        # Get aggregate data for filters
        price_range = products.aggregate(min=Min('price'), max=Max('price'))
        brands = products.values_list('brand', flat=True).distinct()
        categories = dict(Products.Categories.choices)
        
        # Apply filters
        filtered_products = filterset.qs
        
        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get('page_size', 10))  # Default 10 items per page
        paginated_queryset = paginator.paginate_queryset(filtered_products, request)
        
        serializer = SzProducts(paginated_queryset, many=True)
        
        # Get the paginated response
        pagination_data = {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'current_page': paginator.page.number,
            'total_pages': paginator.page.paginator.num_pages,
        }
        
        return Response({
            'data': serializer.data,
            'pagination': pagination_data,
            'metadata': {
                'price_range': price_range,
                'available_brands': list(brands),
                'available_categories': categories,
            }
        })

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = request.user.profile
        type_user = profile.user_type
        print(profile)
        print(type_user)

        # تحقق من وجود Profile وكونه Vendor
        try:
            
            if type_user != 'vendor':
                return Response(
                    {"detail": "Only vendors can add products."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Profile.DoesNotExist:
            return Response(
                {"detail": "Profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # استكمال إنشاء المنتج
        data = request.data.copy()
        data['user'] = user.id
        serializer = SzProducts(data=data)

        if serializer.is_valid():
            product = serializer.save(user=user)
            post_serializer = SzProducts(product, many=False)
            return Response({'product': post_serializer.data})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        if product.user != request.user:
            return Response({'error': 'you dont have permission to edit this item'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SzProducts(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            return Response({'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        product = get_object_or_404(Products, id=pk)
        if product.user != request.user:
            return Response({'error': 'you dont have permission to delete this item'}, status=status.HTTP_403_FORBIDDEN)
        product.delete()
        return Response({'result': 'The product has been deleted'}, status=status.HTTP_200_OK)

class RecommendedProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recommended_products = get_recommended_products(request.user)
        serializer = SzProducts(recommended_products, many=True)
        return Response(serializer.data)




