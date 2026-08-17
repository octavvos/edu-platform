from rest_framework import permissions, viewsets

from .models import Enrollment
from .serializers import EnrollmentSerializer


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
