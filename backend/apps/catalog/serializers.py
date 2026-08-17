from rest_framework import serializers

from .models import Category, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent", "order")


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "course", "user", "user_name", "rating", "comment", "is_published", "created_at")
        read_only_fields = ("id", "user", "is_published", "created_at")
