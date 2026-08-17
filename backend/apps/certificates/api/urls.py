from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CertificateVerifyView, CertificateViewSet

router = DefaultRouter()
router.register(r"certificates", CertificateViewSet, basename="certificate")

urlpatterns = router.urls + [
    path("verify/<str:code>/", CertificateVerifyView.as_view(), name="certificate-verify"),
]
