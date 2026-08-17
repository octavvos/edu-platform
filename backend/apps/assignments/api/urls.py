from rest_framework.routers import DefaultRouter

from .views import HomeworkViewSet, SubmissionViewSet

router = DefaultRouter()
router.register(r"homeworks", HomeworkViewSet, basename="homework")
router.register(r"submissions", SubmissionViewSet, basename="submission")

urlpatterns = router.urls
