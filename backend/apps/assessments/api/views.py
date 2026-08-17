from rest_framework import permissions, viewsets

from apps.assessments.models import Attempt
from apps.assessments.serializers import AttemptSerializer


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """T-04: foydalanuvchining o'z urinishlar tarixi."""

    serializer_class = AttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["lesson"]

    def get_queryset(self):
        return Attempt.objects.filter(user=self.request.user).select_related("lesson")
