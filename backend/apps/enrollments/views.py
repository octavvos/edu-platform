from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import Enrollment, Progress
from .serializers import EnrollmentSerializer, ProgressSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "status"]

    def get_queryset(self):
        user = self.request.user
        qs = Enrollment.objects.select_related("student", "course")
        if user.is_admin:
            return qs
        if user.is_teacher:
            return qs.filter(course__teacher=user)
        return qs.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["post"], url_path="progress")
    def report_progress(self, request, pk=None):
        """Pleyer/dars sahifasidan: {"lesson": id, "status": "completed", "seconds_watched": 120}."""
        enrollment = self.get_object()
        lesson_id = request.data.get("lesson")
        status_value = request.data.get("status", Progress.Status.IN_PROGRESS)
        seconds_watched = int(request.data.get("seconds_watched", 0) or 0)
        last_position = int(request.data.get("last_position", 0) or 0)

        from apps.courses.models import Lesson

        lesson = Lesson.objects.filter(pk=lesson_id, module__course=enrollment.course).first()
        if not lesson:
            return Response({"detail": "Dars topilmadi."}, status=404)

        progress = services.mark_lesson_progress(
            enrollment=enrollment, lesson=lesson, status=status_value,
            seconds_watched=seconds_watched, last_position=last_position,
        )
        enrollment.refresh_from_db()
        return Response({
            "progress": ProgressSerializer(progress).data,
            "enrollment_progress_percent": enrollment.progress_percent,
        })
