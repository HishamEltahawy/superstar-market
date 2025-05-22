from django.urls import path
from . import views
from .  import views  

urlpatterns = [
# Cart API Endpoints
# http://127.0.0.1:5050/api/cart/
path('show-cart/', views.CartView.as_view(), name='cart'),
path('cart/items/', views.CartItemView.as_view(), name='cart_items'),
path('cart/items/<uuid:product_id>/', views.CartItemView.as_view(), name='remove_cart_item'),
]