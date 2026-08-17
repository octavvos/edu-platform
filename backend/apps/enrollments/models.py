import uuid

from django.conf import settings
from django.db import models

from apps.courses.models import Course, Lesson


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    class AccessType(models.TextChoices):
        PURCHASED = "purchased", "Sotib olingan"
        FREE = "free", "Bepul"
        GIFTED = "gifted", "Sovg'a qilingan"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments",
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    access_type = models.CharField(max_length=20, choices=AccessType.choices, default=AccessType.FREE)

    # G-02: denormalizatsiya — tez o'qish uchun
    progress_percent = models.PositiveSmallIntegerField(default=0)
    completed_lessons_count = models.PositiveIntegerField(default=0)

    starts_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-starts_at"]

    def __str__(self):
        return f"{self.student} -> {self.course}"

    @property
    def owner(self):
        return self.student

    @property
    def enrolled_at(self):
        return self.starts_at


class Progress(models.Model):
    """G-01/G-02: dars darajasidagi progress — Enrollment.progress_percent shundan hisoblanadi."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Boshlanmagan"
        IN_PROGRESS = "in_progress", "Jarayonda"
        COMPLETED = "completed", "Tugallangan"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="progress_records")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress_records")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    seconds_watched = models.PositiveIntegerField(default=0)
    last_position = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("enrollment", "lesson")

    def __str__(self):
        return f"{self.enrollment} / {self.lesson} ({self.status})"


class DripRule(models.Model):
    """C-05: darslarni jadval/shart bo'yicha bosqichma-bosqich ochish qoidasi."""

    class RuleType(models.TextChoices):
        DATE = "date", "Sanaga bog'liq"
        PREVIOUS_LESSON = "previous_lesson", "Oldingi darsni tugatgandan keyin"
        MIN_SCORE = "min_score", "Testdan minimal ball to'plagandan keyin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="drip_rule")
    rule_type = models.CharField(max_length=20, choices=RuleType.choices)
    unlock_at = models.DateTimeField(null=True, blank=True)
    min_score_percent = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"DripRule({self.lesson}, {self.rule_type})"
