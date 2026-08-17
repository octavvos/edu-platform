from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LedgerViewSet, OrderViewSet, PaymeWebhookView, PromoValidateView

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"ledger", LedgerViewSet, basename="ledger")

urlpatterns = router.urls + [
    path("promo/validate/", PromoValidateView.as_view(), name="promo-validate"),
    path("webhooks/payme/", PaymeWebhookView.as_view(), name="payme-webhook"),
]
