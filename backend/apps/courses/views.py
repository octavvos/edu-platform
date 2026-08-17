from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.assessments import services as assessment_services
from apps.rbac.services import has_permission

from . import services
from .models import Course, Lesson, Module
from .permissions import IsTeacherOrReadOnly
from .serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
    LessonSerializer,
    ModuleListSerializer,
    ModuleSerializer,
)
from .selectors import visible_lessons_for_user


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("teacher", "category").prefetch_related("modules")
    permission_classes = [IsTeacherOrReadOnly]
    filterset_fields = ["level", "status", "teacher", "category"]
    search_fields = ["title", "description"]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action in ("list",):
            return CourseListSerializer
        return CourseDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if self.request.method in ("GET", "HEAD", "OPTIONS") and self.action in ("list",):
            if not (user.is_authenticated and (user.is_admin or has_permission(user, "course.moderate"))):
                # Mehmon/o'quvchi uchun faqat nashr etilgan kurslar + o'zining qoralamalari (agar teacher)
                from django.db.models import Q
                visible = Q(status=Course.Status.PUBLISHED)
                if user.is_authenticated:
                    visible |= Q(teacher=user)
                qs = qs.filter(visible)
        return qs

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

    @action(detail=True, methods=["post"], url_path="submit-for-moderation")
    def submit_for_moderation(self, request, pk=None):
        course = self.get_object()
        if course.teacher_id != request.user.id and not request.user.is_admin:
            return Response({"detail": "Ruxsat yo'q."}, status=403)
        course = services.submit_for_moderation(course=course)
        return Response(CourseDetailSerializer(course).data)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        if not (request.user.is_admin or has_permission(request.user, "course.publish")):
            return Response({"detail": "Ruxsat yo'q."}, status=403)
        course = self.get_object()
        course = services.publish_course(course=course, moderator=request.user)
        return Response(CourseDetailSerializer(course).data)


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
        base = Lesson.objects.select_related("module", "module__course", "module__course__teacher")
        return visible_lessons_for_user(base, self.request.user)

    @action(detail=True, methods=["post"], url_path="check-quiz", permission_classes=[AllowAny])
    def check_quiz(self, request, pk=None):
        lesson = self.get_object()
        answers = request.data.get("answers", {})

        if request.user.is_authenticated:
            attempt = assessment_services.grade_quiz(user=request.user, lesson=lesson, answers=answers)
            correct, total = attempt.score, attempt.total
        else:
            # Mehmon uchun ham darhol natija (Attempt saqlanmaydi — bepul preview darslar uchun)
            questions = list(lesson.questions.prefetch_related("choices"))
            total = len(questions)
            correct = sum(
                1 for q in questions
                if assessment_services._check_answer(q, answers.get(str(q.id)))
            )

        correct_choices = assessment_services.correct_choice_map(lesson)
        return Response({"total": total, "correct": correct, "correct_choices": correct_choices})
