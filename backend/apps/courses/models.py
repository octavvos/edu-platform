import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    class Status(models.TextChoices):
        """C-02: qoralama / moderatsiyada / nashr etilgan."""

        DRAFT = "draft", "Qoralama"
        MODERATION = "moderation", "Moderatsiyada"
        PUBLISHED = "published", "Nashr etilgan"
        REJECTED = "rejected", "Rad etilgan"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="courses/covers/", null=True, blank=True)
    trailer_video_url = models.URLField(blank=True)

    category = models.ForeignKey(
        "catalog.Category", on_delete=models.SET_NULL, related_name="courses", null=True, blank=True,
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses_taught",
    )

    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    language = models.CharField(max_length=10, default="uz")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="UZS")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    organization_id = models.UUIDField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def owner(self):
        return self.teacher

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course.title} / {self.title}"

    @property
    def owner(self):
        return self.course.teacher


class Lesson(models.Model):
    class ContentType(models.TextChoices):
        VIDEO = "video", "Video dars"
        TEXT = "text", "Matnli dars"
        FILE = "file", "Fayl / material"
        QUIZ = "quiz", "Test / kviz"
        HOMEWORK = "homework", "Uy vazifasi"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.TEXT)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    is_required = models.BooleanField(default=True)  # C-06
    is_free_preview = models.BooleanField(default=False)  # K-07

    # C-05: drip-content shartlari, masalan {"unlock_at": "...", "min_score": 70}
    unlock_rule = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.module.title} / {self.title}"

    @property
    def owner(self):
        return self.module.course.teacher


class VideoAsset(models.Model):
    """
    V-01..V-10 / D-11: video provayder abstraksiyasi. MVP'da haqiqiy
    Bunny Stream integratsiyasi ulanmagan (I-03 — sizning hisobingiz
    kerak); `provider="manual"` bilan to'g'ridan-to'g'ri video_url
    ishlatiladi. Kelayotgan real integratsiya faqat shu model va
    `apps.courses.video_providers` ichida almashadi — Lesson yoki API
    o'zgarmaydi.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Yuklanmoqda"
        PROCESSING = "processing", "Transkodlanmoqda"
        READY = "ready", "Tayyor"
        FAILED = "failed", "Xatolik"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="video_asset")
    provider = models.CharField(max_length=30, default="manual")
    external_id = models.CharField(max_length=255, blank=True)
    manifest_url = models.URLField(blank=True)  # HLS .m3u8
    duration_seconds = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"VideoAsset({self.lesson_id}, {self.status})"
