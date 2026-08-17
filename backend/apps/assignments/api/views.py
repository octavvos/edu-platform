from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.assignments import services
from apps.assignments.models import Homework, Submission
from apps.assignments.serializers import (
    GradeSubmissionSerializer,
    HomeworkSerializer,
    SubmissionSerializer,
)


class IsTeacherOrMentorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and (user.is_teacher or user.is_mentor or user.is_admin))


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.select_related("lesson")
    serializer_class = HomeworkSerializer
    filterset_fields = ["lesson"]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsTeacherOrMentorOrAdmin()]


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["homework", "status"]

    def get_queryset(self):
        user = self.request.user
        qs = Submission.objects.select_related("homework", "student", "mentor")
        if user.is_admin:
            return qs
        if user.is_teacher or user.is_mentor:
            return qs.filter(homework__lesson__module__course__teacher=user) | qs.filter(mentor=user)
        return qs.filter(student=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        homework = serializer.validated_data["homework"]
        submission = services.submit_homework(
            student=request.user, homework=homework,
            content=serializer.validated_data.get("content", ""),
            file=serializer.validated_data.get("file"),
            link=serializer.validated_data.get("link", ""),
        )
        return Response(self.get_serializer(submission).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsTeacherOrMentorOrAdmin])
    def grade(self, request, pk=None):
        submission = self.get_object()
        serializer = GradeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = services.grade_submission(
            submission=submission, mentor=request.user, **serializer.validated_data,
        )
        return Response(SubmissionSerializer(submission).data)
