import uuid
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver


# Create your models here.
class Categories(models.TextChoices):
    COMPUTER = 'Computer'
    FOOD = 'Food'
    KIDS = 'Kids'
    HOME = 'Home'

class Products(models.Model):
    id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='', blank=False)
    image = models.ImageField( blank=True, null=True, upload_to='ProductsApp/images/%Y/%m/%d/')
    description = models.TextField(max_length=1000, default='', blank=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=False, default=0.00)
    brand = models.CharField(max_length=200, default='', blank=False)
    category = models.CharField(max_length=50, choices=Categories.choices)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    review_count = models.IntegerField(default=0, blank=True, null=True)  # عدد المراجعات
    def __str__(self):
        return self.name
    
