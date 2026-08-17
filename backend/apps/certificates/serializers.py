from rest_framework import serializers

from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="enrollment.course.title", read_only=True)
    student_name = serializers.CharField(source="enrollment.student.get_full_name", read_only=True)

    class Meta:
        model = Certificate
        fields = ("id", "code", "course_title", "student_name", "pdf_file", "issued_at")
        read_only_fields = fields


class CertificateVerifySerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="enrollment.course.title", read_only=True)
    student_name = serializers.CharField(source="enrollment.student.get_full_name", read_only=True)
    teacher_name = serializers.CharField(source="enrollment.course.teacher.get_full_name", read_only=True)

    class Meta:
        model = Certificate
        fields = ("code", "course_title", "student_name", "teacher_name", "issued_at")
