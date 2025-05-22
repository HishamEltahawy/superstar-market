from rest_framework import serializers
from ReviewsApp.serializers import SzReview
from .models import Products
class SzProducts(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)
    publisher = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Products
        # fields = '__all__'
        fields = ['id', 'name', 'image', 'description', 'price', 'brand', 'category', 'rating', 'stock', 'created_at', 'publisher', 'reviews']
        read_only_fields = ['id'] 
    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = SzReview(reviews, many=True)
        return serializer.data
