from django.contrib import admin
from django.urls import include, path

api_v1_patterns = [
    path("auth/", include("apps.accounts.api.urls")),
    path("", include("apps.catalog.api.urls")),
    path("", include("apps.courses.urls")),
    path("", include("apps.enrollments.urls")),
    path("", include("apps.assessments.api.urls")),
    path("", include("apps.assignments.api.urls")),
    path("", include("apps.certificates.api.urls")),
    path("", include("apps.payments.api.urls")),
    path("", include("apps.notifications.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
    # Eski frontend build'lar/integratsiyalar uchun versiyasiz alias (5.6-band: /api/v1/ asosiy)
    path("api/", include(api_v1_patterns)),
]
