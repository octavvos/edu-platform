import uuid

from django.conf import settings
from django.db import models


class Question(models.Model):
    """4.6-band: savol turlari (MVP — 4 ta)."""

    class QuestionType(models.TextChoices):
        SINGLE = "single", "Bitta to'g'ri javob"
        MULTIPLE = "multiple", "Bir nechta to'g'ri javob"
        TRUE_FALSE = "true_false", "To'g'ri/noto'g'ri"
        SHORT_TEXT = "short_text", "Qisqa matnli javob"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QuestionType.choices, default=QuestionType.SINGLE)
    # T-06: noto'g'ri javob uchun izoh
    explanation = models.TextField(blank=True)
    # SHORT_TEXT uchun: aniq moslik yoki regex
    expected_answer_pattern = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:60]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:60]


class Attempt(models.Model):
    """T-04: urinishlar soni, o'tish balli (%)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, related_name="attempts")
    score = models.PositiveSmallIntegerField(default=0)
    total = models.PositiveSmallIntegerField(default=0)
    score_percent = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} / {self.lesson} ({self.score}/{self.total})"


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name="selected_in_answers")
    text_answer = models.CharField(max_length=255, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("attempt", "question")
