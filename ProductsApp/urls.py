from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    ProductListView,
    ProductDetailView,
    FilteredProductsView,
    FilteredProductsPaginatedView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    RecommendedProductsView
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('product/<str:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('filtered/', FilteredProductsView.as_view(), name='filtered-products'),
    path('filtered-pages/', FilteredProductsPaginatedView.as_view(), name='filtered-products-paginated'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('update/<str:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('delete/<str:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('recommended/', RecommendedProductsView.as_view(), name='recommended-products'),
]
