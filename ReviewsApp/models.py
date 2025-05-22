from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from ProductsApp.models import Products

# Create your models here.
class Reviews(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000, default='', blank=False)
    rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # منع المراجعات المكررة

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"

@receiver(post_save, sender=Reviews)
@receiver(post_delete, sender=Reviews)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    reviews = product.reviews.all()
    if reviews.exists():
        product.rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    else:
        product.rating = 0  # إذا لم تكن هناك مراجعات
    product.save()
    
@receiver(post_save, sender=Reviews)
@receiver(post_delete, sender=Reviews)
def update_review_count(sender, instance, **kwargs):
    product = instance.product
    product.review_count = product.reviews.count()
    product.save()