from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ProductsApp.models import Products
from .models import Cart, CartItem
import uuid

class CartTests(APITestCase):
    def setUp(self):
        # Create test user and vendor
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='vendor123'
        )
        
        # Create test product
        self.product = Products.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            stock=10,
            id=uuid.uuid4(),
            user=self.vendor,  # Add vendor as product owner
            brand='Test Brand',
            category='Computer'
        )
        
        # URLs
        self.cart_url = reverse('cart')
        self.cart_items_url = reverse('cart_items')
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_add_item_to_cart(self):
        """Test adding an item to the cart"""
        data = {
            'product_id': str(self.product.id),
            'quantity': 2
        }
        
        response = self.client.post(self.cart_items_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.first().quantity, 2)
    
    def test_add_item_exceeding_stock(self):
        """Test adding item with quantity exceeding stock"""
        data = {
            'product_id': str(self.product.id),
            'quantity': 20  # Stock is only 10
        }
        
        response = self.client.post(self.cart_items_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot add 20 items', str(response.data))
    
    def test_add_nonexistent_product(self):
        """Test adding non-existent product to cart"""
        data = {
            'product_id': str(uuid.uuid4()),  # Random UUID
            'quantity': 1
        }
        
        response = self.client.post(self.cart_items_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Product not found', str(response.data))
    
    def test_update_cart_item_quantity(self):
        """Test updating quantity of cart item"""
        # First add item to cart
        cart_item = CartItem.objects.create(
            cart=self.user.cart,
            product=self.product,
            quantity=1
        )
        
        # Update quantity
        update_url = f'/api/cart/items/{self.product.id}/'
        data = {'quantity': 3}
        
        response = self.client.patch(update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.first().quantity, 3)
