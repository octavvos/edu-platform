from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = router.urls
