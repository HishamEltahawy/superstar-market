from django.urls import path
from django.conf import settings
from .views import (
    ReviewCreateView,
    ProductReviewsView,
    ReviewDeleteView,

)

urlpatterns = [
path('review/<str:pk>/', ReviewCreateView.as_view(), name='review-create'),
path('reviews/<str:pk>/', ProductReviewsView.as_view(), name='product-reviews'),
path('review/delete/<str:pk>/', ReviewDeleteView.as_view(), name='review-delete'),
]