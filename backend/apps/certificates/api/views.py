from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.certificates.models import Certificate
from apps.certificates.serializers import CertificateSerializer, CertificateVerifySerializer


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """U-04: sertifikatlar arxivi."""

    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(enrollment__student=self.request.user).select_related(
            "enrollment__course", "enrollment__student",
        )


class CertificateVerifyView(APIView):
    """G-05: ochiq verifikatsiya sahifasi — /verify/{code}."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, code):
        certificate = Certificate.objects.filter(code=code).select_related(
            "enrollment__course", "enrollment__student", "enrollment__course__teacher",
        ).first()
        if not certificate:
            return Response({"detail": "Sertifikat topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CertificateVerifySerializer(certificate).data)
