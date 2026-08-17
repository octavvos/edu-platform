from rest_framework import serializers

from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            "id", "student", "student_username", "course", "course_title",
            "status", "progress_percent", "enrolled_at", "completed_at",
        )
        read_only_fields = ("id", "student", "enrolled_at")

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)
