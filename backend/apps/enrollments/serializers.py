from rest_framework import serializers

from .models import Enrollment, Progress


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            "id", "student", "student_username", "course", "course_title",
            "status", "access_type", "progress_percent", "completed_lessons_count",
            "starts_at", "completed_at",
        )
        read_only_fields = ("id", "student", "progress_percent", "completed_lessons_count", "starts_at")

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class ProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Progress
        fields = (
            "id", "enrollment", "lesson", "lesson_title", "status",
            "seconds_watched", "last_position", "completed_at", "updated_at",
        )
        read_only_fields = ("id", "updated_at")
