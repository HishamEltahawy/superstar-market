from rest_framework import serializers
from .models import Reviews

class SzReview(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # عرض اسم المستخدم بدلاً من الـ ID
    product = serializers.StringRelatedField()  # عرض اسم المنتج بدلاً من الـ ID
    class Meta:
        model = Reviews
        fields = '__all__'

