from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, LessonViewSet, ModuleViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"modules", ModuleViewSet, basename="module")
router.register(r"lessons", LessonViewSet, basename="lesson")

urlpatterns = router.urls
