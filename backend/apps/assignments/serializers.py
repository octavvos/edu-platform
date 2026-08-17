from rest_framework import serializers

from .models import Homework, Submission


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ("id", "lesson", "instructions", "deadline", "max_score", "created_at")
        read_only_fields = ("id", "created_at")


class SubmissionSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    homework_lesson_title = serializers.CharField(source="homework.lesson.title", read_only=True)

    class Meta:
        model = Submission
        fields = (
            "id", "homework", "homework_lesson_title", "student", "student_username", "mentor",
            "content", "file", "link", "status", "score", "feedback", "is_late", "submitted_at", "reviewed_at",
        )
        read_only_fields = (
            "id", "student", "mentor", "status", "score", "feedback",
            "is_late", "submitted_at", "reviewed_at",
        )

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class GradeSubmissionSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0, max_value=100)
    feedback = serializers.CharField(allow_blank=True, required=False)
    status = serializers.ChoiceField(choices=[Submission.Status.ACCEPTED, Submission.Status.NEEDS_REVISION])
