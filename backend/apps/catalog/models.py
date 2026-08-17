import uuid

from django.conf import settings
from django.db import models


class Category(models.Model):
    """K-01: kategoriya va subkategoriyalar (2 daraja)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", null=True, blank=True,
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.parent.name} / {self.name}" if self.parent else self.name

    def save(self, *args, **kwargs):
        if self.parent_id and self.parent.parent_id:
            raise ValueError("Kategoriya faqat 2 darajali bo'lishi mumkin (subkategoriya ota bo'la olmaydi).")
        super().save(*args, **kwargs)


class Review(models.Model):
    """K-08: sharh va reyting — faqat kursni sotib olganlar, moderatsiyadan keyin nashr etiladi."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.course} ({self.rating}★)"
