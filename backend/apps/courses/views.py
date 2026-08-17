from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Lesson, Module
from .permissions import IsTeacherOrReadOnly
from .serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
    LessonSerializer,
    ModuleListSerializer,
    ModuleSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("teacher").prefetch_related("modules")
    permission_classes = [IsTeacherOrReadOnly]
    filterset_fields = ["level", "is_published", "teacher"]
    search_fields = ["title", "description"]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action in ("list",):
            return CourseListSerializer
        return CourseDetailSerializer

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="modules")
    def modules(self, request, pk=None):
        course = self.get_object()
        if request.method == "POST":
            serializer = ModuleSerializer(data={**request.data, "course": course.id})
            serializer.is_valid(raise_exception=True)
            serializer.save(course=course)
            return Response(serializer.data, status=201)

        qs = course.modules.all()
        serializer = ModuleListSerializer(qs, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related("course", "course__teacher").prefetch_related("lessons")
    serializer_class = ModuleSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filterset_fields = ["course"]

    @action(detail=True, methods=["get", "post"], url_path="lessons")
    def lessons(self, request, pk=None):
        module = self.get_object()
        if request.method == "POST":
            serializer = LessonSerializer(data={**request.data, "module": module.id})
            serializer.is_valid(raise_exception=True)
            serializer.save(module=module)
            return Response(serializer.data, status=201)

        qs = module.lessons.all()
        serializer = LessonSerializer(qs, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filterset_fields = ["module"]

    def get_queryset(self):
        qs = Lesson.objects.select_related("module", "module__course", "module__course__teacher")
        user = self.request.user

        if not user.is_authenticated:
            return qs.filter(is_free_preview=True)
        if user.is_admin:
            return qs

        from apps.enrollments.models import Enrollment

        enrolled_course_ids = Enrollment.objects.filter(
            student=user, status=Enrollment.Status.ACTIVE
        ).values_list("course_id", flat=True)

        return qs.filter(
            Q(is_free_preview=True)
            | Q(module__course__teacher=user)
            | Q(module__course_id__in=enrolled_course_ids)
        )
