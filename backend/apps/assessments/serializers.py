from rest_framework import serializers

from .models import Attempt, Choice, Question


class ChoicePublicSerializer(serializers.ModelSerializer):
    """`is_correct` server-side'da qoladi — faqat check-quiz orqali baholanadi (T-05)."""

    class Meta:
        model = Choice
        fields = ("id", "text")


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoicePublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "question_type", "choices")


class ChoiceAuthoringSerializer(serializers.ModelSerializer):
    """O'qituvchi uchun — is_correct ko'rinadi va yoziladi."""

    class Meta:
        model = Choice
        fields = ("id", "question", "text", "is_correct", "order")


class QuestionAuthoringSerializer(serializers.ModelSerializer):
    choices = ChoiceAuthoringSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "lesson", "text", "question_type", "explanation", "order", "choices")


class AttemptSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Attempt
        fields = ("id", "lesson", "lesson_title", "score", "total", "score_percent", "started_at", "submitted_at")
        read_only_fields = fields
