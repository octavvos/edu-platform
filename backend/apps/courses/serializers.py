from rest_framework import serializers

from apps.assessments.serializers import QuestionSerializer

from .models import Course, Lesson, Module


class LessonSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    has_homework = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id", "module", "title", "content_type", "content",
            "video_url", "duration_minutes", "order", "is_required",
            "is_free_preview", "questions", "has_homework", "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_has_homework(self, obj):
        return hasattr(obj, "homework")


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


class LessonBriefSerializer(serializers.ModelSerializer):
    """Lesson summary without `content`/`video_url` — safe to expose on the course page before enrollment."""

    class Meta:
        model = Lesson
        fields = (
            "id", "module", "title", "content_type", "duration_minutes",
            "order", "is_required", "is_free_preview",
        )


class ModuleWithLessonsSerializer(serializers.ModelSerializer):
    lessons = LessonBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ("id", "course", "title", "order", "lessons")


class CourseListSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    modules_count = serializers.IntegerField(source="modules.count", read_only=True)
    is_published = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id", "title", "slug", "description", "cover_image",
            "category", "category_name", "teacher", "teacher_name",
            "level", "price", "currency", "status", "is_published",
            "modules_count", "created_at",
        )
        read_only_fields = ("id", "slug", "teacher", "status", "created_at")


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleWithLessonsSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_published = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id", "title", "slug", "description", "cover_image", "trailer_video_url",
            "category", "category_name", "teacher", "teacher_name",
            "level", "language", "price", "currency", "status", "is_published",
            "modules", "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "teacher", "status", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["teacher"] = self.context["request"].user
        return super().create(validated_data)
