
from django.urls import path, include, re_path
from . import views as view
urlpatterns = [
       path('wishlist/', view.WishlistView.as_view(), name='wishlist'), # wishlist/
]