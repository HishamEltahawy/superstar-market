from django.db import models
from django.contrib.auth.models import User
from ProductsApp.models import Products
# Create your models here.


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Products, related_name='wishlisted_by')

    def __str__(self):
        return f"Wishlist of {self.user.username}"
