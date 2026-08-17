from rest_framework import serializers

from .models import Course, Lesson, Module


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id", "module", "title", "content_type", "content",
            "video_url", "duration_minutes", "order", "is_free_preview",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ("id", "course", "title", "order", "lessons", "created_at")
        read_only_fields = ("id", "created_at")


class ModuleListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)

    class Meta:
        model = Module
        fields = ("id", "course", "title", "order", "lessons_count")
        read_only_fields = ("id",)


class CourseListSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    modules_count = serializers.IntegerField(source="modules.count", read_only=True)

    class Meta:
        model = Course
        fields = (
            "id", "title", "slug", "description", "cover_image",
            "teacher", "teacher_name", "level", "price", "is_published",
            "modules_count", "created_at",
        )
        read_only_fields = ("id", "slug", "teacher", "created_at")


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleListSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)

    class Meta:
        model = Course
        fields = (
            "id", "title", "slug", "description", "cover_image",
            "teacher", "teacher_name", "level", "price", "is_published",
            "modules", "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "teacher", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["teacher"] = self.context["request"].user
        return super().create(validated_data)
