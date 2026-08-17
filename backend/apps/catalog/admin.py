from django.contrib import admin

from .models import Category, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "order")
    list_filter = ("parent",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "rating", "is_published", "created_at")
    list_filter = ("is_published", "rating")
    actions = ["publish_reviews"]

    @admin.action(description="Tanlangan sharhlarni nashr etish")
    def publish_reviews(self, request, queryset):
        queryset.update(is_published=True)
