import uuid

from django.conf import settings
from django.db import models


class Homework(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField("courses.Lesson", on_delete=models.CASCADE, related_name="homework")
    instructions = models.TextField()
    deadline = models.DateTimeField(null=True, blank=True)  # H-05
    max_score = models.PositiveSmallIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Homework({self.lesson})"


class Submission(models.Model):
    """H-03: yuborilgan -> tekshirilmoqda -> qayta ishlashga qaytarildi -> qabul qilindi."""

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Yuborilgan"
        UNDER_REVIEW = "under_review", "Tekshirilmoqda"
        NEEDS_REVISION = "needs_revision", "Qayta ishlashga qaytarildi"
        ACCEPTED = "accepted", "Qabul qilindi"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="homework_submissions",
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="homework_to_grade",
        null=True, blank=True,
    )

    content = models.TextField(blank=True)
    file = models.FileField(upload_to="submissions/", null=True, blank=True)
    link = models.URLField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    score = models.PositiveSmallIntegerField(null=True, blank=True)  # H-04: 0-100
    feedback = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)  # H-05

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student} -> {self.homework} ({self.status})"
